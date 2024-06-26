from .models import *
from django.utils import timezone
import pandas as pd
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from glossary.models import Glossary
from django.core.cache import cache
from django.db.models import Prefetch   

import logging
log =  logging.getLogger('log')


def get_all_questions():  
    """
    Retrieve and cache all Question instances.

    This function fetches all Question instances from the database and caches the result for better performance on
    subsequent calls.

    Returns:
        QuerySet: A QuerySet containing all Question instances.
    """             
    questions = cache.get('all_questions') 
    if not questions:
        questions = Question.objects.all().select_related('parent_question').prefetch_related('stanchart', 'question')
        cache.set('all_questions', questions, 3600)
    return questions

def get_all_stdoils():
    """
    Retrieve and cache all StdOils instances.

    This function fetches all StdOils instances from the database and caches the result for better performance on
    subsequent calls.

    Returns:
        QuerySet: A QuerySet containing all StdOils instances.
    """
    stdoils = cache.get('all_stdoils')
    if not stdoils:
        stdoils = StdOils.objects.all().select_related('select_oil', 'biofuel')
        cache.set('all_stdoils', stdoils, 3600)
    return stdoils

def get_all_glosaries():
    """
    Retrieve and cache all Glossary instances.

    This function fetches all Glossary instances from the database and caches the result for better performance on
    subsequent calls.

    Returns:
        QuerySet: A QuerySet containing all Glossary instances.
    """
    glosaries = cache.get('all_glosaries')
    if not glosaries:
        glosaries = Glossary.objects.all()
        cache.set('all_glosaries', glosaries, 3600)
    return glosaries

def get_all_definedlabel():
    """
    Retrieve and cache all DifinedLabel instances.

    This function fetches all DifinedLabel instances from the database and caches the result for better performance on
    subsequent calls.

    Returns:
        QuerySet: A QuerySet containing all DifinedLabel instances.
    """
    definedlabel = cache.get('all_definedlabel')
    if not definedlabel:
        definedlabel = DifinedLabel.objects.all().prefetch_related('user_label')
        cache.set('all_definedlabel', definedlabel, 3600)
    return definedlabel
 
def get_all_reports_with_last_answer(request, first_of_parent):
    """
    Retrieve and cache all reports with their last answered question.

    This function fetches all reports (evaluators) and their corresponding evaluations, including the last answered
    question, and caches the result for better performance on subsequent calls.

    Args:
        request: The HTTP request object.
        first_of_parent: The first question of the parent questionnaire.

    Returns:
        QuerySet: A QuerySet containing all reports (evaluators) with their last answered question.
    """
    
    user = request.user    

    if user.is_superuser or user.is_staff:
        reports = Evaluator.objects.all().order_by('-id').prefetch_related(
            Prefetch(
                'eva_evaluator', 
                queryset=Evaluation.objects.order_by('-id')
                .select_related('question')
                )
            ).select_related('creator')       
    else:
        reports = Evaluator.objects.filter(creator=user).order_by('-id').prefetch_related(
            Prefetch(
                'eva_evaluator', 
                queryset=Evaluation.objects.order_by('-id')
                .select_related('question')
                )
            ).select_related('creator')

    for report in reports:
        evaluation = report.eva_evaluator.first()     
        if report is not None:            
            try:               
                last_question = evaluation.question
                setattr(report, 'last_slug', last_question.slug)
            except Exception as e:                
                setattr(report, 'last_slug', first_of_parent.slug)
                continue
    
    return reports


def get_biofuel():    
    """
    Retrieve and cache all Biofuel instances.

    This function fetches all Biofuel instances from the database and caches the result for better performance on
    subsequent calls.

    Returns:
        QuerySet: A QuerySet containing all Biofuel instances.
    """
    biofuels = cache.get('all_biofuels')
    if not biofuels:
        biofuels = Biofuel.objects.all().prefetch_related('eva_fuel')
        cache.set('all_biofuels', biofuels, 3600)
    return biofuels

def get_options_of_ques(question):     
    """
    Retrieve and cache all options for a given question.

    This function fetches all Option instances related to a specific question and caches the result for better
    performance on subsequent calls.

    Args:
        question (Question): The question for which to retrieve options.

    Returns:
        QuerySet: A QuerySet containing all options for the given question.
    """
    options = cache.get(f'options_of_ques_{question.id}')
    if not options:
        options = question.question.all()
        cache.set(f'options_of_ques_{question.id}', options, 3600)
        
    return options


def get_sugestions_of_ques(question):    
    """
    Retrieve and cache all suggestions for a given question.

    This function fetches all Suggestions instances related to a specific question, orders them by creation date, and
    caches the result for better performance on subsequent calls.

    Args:
        question (Question): The question for which to retrieve suggestions.

    Returns:
        QuerySet: A QuerySet containing all suggestions for the given question.
    """
    suggestions = cache.get(f'sugestions_of_ques_{question.id}')
    if not suggestions:
        suggestions = question.question_sugestion.all().order_by('-created')
        cache.set(f'sugestions_of_ques_{question.id}', suggestions, 3600)
        
    return suggestions  


def active_sessions():
    """
    Retrieve Active Evaluator IDs from the Past 24 Hours.

    This function collects all active sessions' evaluator IDs from the past 24 hours and returns them as a list.

    Returns:
        list: A list of evaluator IDs from active sessions within the last 24 hours.
    """
    from django.contrib.sessions.models import Session # As it is sensative operation I will call it inside this function only.
        
    # Get sessions that have not expired within the past 24 hours
    sessions = Session.objects.filter(expire_date__gt=(timezone.now() - timezone.timedelta(hours=24)))
    
    # Initialize a set to store unique evaluator IDs
    active_evaluator_ids = set()
    
    # Iterate through active sessions
    for session in sessions:
        session_data = session.get_decoded()
        evaluator_id = session_data.get('evaluator')
        
        # Check if an evaluator ID is present in the session data
        if evaluator_id:
            active_evaluator_ids.add(evaluator_id)
   
    # Convert the set of evaluator IDs to a list
    return list(active_evaluator_ids)  


def clear_evaluator():
    """
    Clear Incomplete Evaluators and Their Related Data

    This function is typically scheduled to run as a background task (e.g., via a CRON job) to remove incomplete
    evaluator records that were initialized but have no associated data and are not qualified for display on the
    user's profile page. It deletes these incomplete evaluators along with their related data to maintain a clean
    database.

    Returns:
        int: The total number of incomplete evaluators deleted in the process.
    """    
    
    # Fetch incomplete evaluators that have not generated a report
    incomplete_evaluators = Evaluator.objects.filter(report_genarated=False)
    
    # Get the IDs of currently active evaluator sessions
    active_evaluator_ids = set(active_sessions())
    
    # Initialize a list to store the IDs of evaluators to be deleted
    evaluators_to_delete = []
    
    # Iterate through incomplete evaluators
    for evaluator in incomplete_evaluators:
        if evaluator.id not in active_evaluator_ids:            
            # Check if the evaluator has no associated data in the evaluation table
            if evaluator.eva_evaluator.count() == 0:
                evaluators_to_delete.append(evaluator.id)
                
    # If there are evaluators to delete
    if evaluators_to_delete:
        total_deleted = len(evaluators_to_delete)
        
        # Delete related data in a specific sequence to avoid foreign key constraints
        # as first related data is beeing saving into the evaluation table so that we will check these table only.
        Evaluation.objects.filter(evaluator__id__in=evaluators_to_delete).delete()
        EvaLebelStatement.objects.filter(evaluator__id__in=evaluators_to_delete).delete()
        EvaLabel.objects.filter(evaluator__id__in=evaluators_to_delete).delete()
        EvaComments.objects.filter(evaluator__id__in=evaluators_to_delete).delete()
        Evaluator.objects.filter(id__in=evaluators_to_delete).delete()

        log.info(f'{total_deleted} incomplete reports with related data have been deleted.')
        
        return total_deleted
    else:
        log.info('No incomplete reports to delete.')
        return 0


def get_current_evaluator(request, evaluator_id = None):
    """
    Get the Current Evaluator.

    This function retrieves the current evaluator object based on the provided `evaluator_id` or the
    `evaluator_id` stored in the user's session. It is assumed that the middleware ensures 'evaluator'
    exists in the session.

    Args:
        request (HttpRequest): The current request object.
        evaluator_id (int, optional): The ID of the evaluator to retrieve. Defaults to None.

    Returns:
        Evaluator: The current evaluator object.

    Example:
        To get the current evaluator from the session:
        ```
        current_evaluator = get_current_evaluator(request)
        # Perform actions with the current evaluator
        ```

        To get a specific evaluator by ID:
        ```
        evaluator_id = 123
        specific_evaluator = get_current_evaluator(request, evaluator_id)
        # Perform actions with the specific evaluator
        ```
    """
    try:
        if evaluator_id:
            evaluator = Evaluator.objects.get(id = evaluator_id)    
        else:   
            evaluator_id_from_session = request.session['evaluator']     
            evaluator = Evaluator.objects.get(id = int(evaluator_id_from_session))   
    except Evaluator.DoesNotExist:
        log.debug(f'No current evaluator found____________it is an important issue!')
        evaluator = None
           
    return evaluator

# def get_all_evaluations_or_on_question(evaluator, question = None):   
#     """
#     Retrieve and cache all evaluations for a given evaluator.

#     This function fetches all Evaluation instances related to a specific evaluator and caches the result for better
#     performance on subsequent calls. Optionally, it can return a single evaluation for a specific question if the
#     'question' parameter is provided.

#     Args:
#         evaluator (Evaluator): The evaluator for whom evaluations are fetched.
#         question (Question, optional): The specific question for which to retrieve an evaluation.

#     Returns:
#         QuerySet or Evaluation: A QuerySet containing all evaluations for the evaluator, or a single Evaluation
#         instance for the specified question (if provided).
#     """ 
#     cache_key = f"{evaluator.id}_evaluations"    
#     evaluations = cache.get(cache_key)
#     if not evaluations:
#         evaluations = Evaluation.objects.filter(
#             evaluator=evaluator).order_by('id').select_related(
#                 'question', 
#                 'option'
#                 )
#         cache.set(cache_key, evaluations, 3600)
        
#     if question:        
#          # If 'question' parameter is provided, return a single evaluation based on the question
#         return next((eva for eva in evaluations if eva.question == question), None)
#     else:
#         # Otherwise, return all evaluations of this report/evaluator
#         return evaluations   



class EvaLebelStatementAnalyzer:
    """
    A class for analyzing evaluation statements related to EvaLebel.

    This class provides methods for analyzing and generating assessment statements
    based on various criteria related to EvaLebel evaluations.

    Args:
        evalebel: An instance of EvaLebel representing the evaluation label.
        evaluator: An instance representing the evaluator.

    Attributes:
        evalebel: An instance of EvaLebel representing the evaluation label.
        evaluator: An instance representing the evaluator.

    Methods:
        get_statement_count(values_key, **filter_kwargs):
            Get the count of distinct statements based on filtering criteria.

        get_dont_know_statement(label_name, value_count):
            Generate a statement based on the value count for "don't know" evaluations.

        get_positive_statement(label_name, value_count):
            Generate a statement based on the value count for positive evaluations.

        ans_to_the_label():
            Get the count of answers related to the evaluation label.

        calculate_percentage(ans_to_the_label):
            Calculate the percentage based on answers related to the evaluation label.

        label_assessment_for_donot_know():
            Generate an assessment statement for "don't know" evaluations related to the label.

        label_assessment_for_positive():
            Generate an assessment statement for positive evaluations related to the label.

        ans_ques():
            Get the count of answerable questions.

        calculate_overall_percent(ans):
            Calculate the overall percentage based on the given count.

        overall_assessment_for_donot_know():
            Generate an overall assessment statement for "don't know" evaluations.

        overall_assessment_for_positive():
            Generate an overall assessment statement for positive evaluations.
    """
    def __init__(self, evalebel, evaluator):
        """
        Initialize a new EvaLebelStatementAnalyzer.

        Args:
            evalebel: An instance of EvaLebel representing the evaluation label.
            evaluator: An instance representing the evaluator.
        """
        self.evalebel = evalebel
        self.evaluator = evaluator
       
        

    def get_statement_count(self, values_key, **filter_kwargs):
        """
        Get the count of distinct statements based on filtering criteria.

        Args:
            values_key: The key to be used for grouping and counting.
            **filter_kwargs: Additional filter criteria as keyword arguments.

        Returns:
            The count of distinct statements based on the given filter criteria.
        """
        counted = (
            EvaLebelStatement.objects
            .filter(**filter_kwargs)
            .values(values_key)
            .distinct()
            .count()
        )
        return counted    
    

    def get_dont_know_statement(self, label_name, value_count): 
        """
        Generate a statement based on the value count for "don't know" evaluations.

        Args:
            label_name: The name of the evaluation label.
            value_count: The count of "don't know" evaluations.

        Returns:
            A statement describing the assessment based on the value count.
        """   
        if value_count < 20:
            statement = f'{label_name} assessment of your biofuel shows that you have very detailed knowledge.'
        elif value_count < 35:
            statement = f'{label_name} assessment of your biofuel shows that you have very significant knowledge.'
        elif value_count < 50:
            statement = f'{label_name} assessment of your biofuel shows that you have very limited knowledge.'
        else:
            statement = f'{label_name} assessment of your biofuel shows that you have very rudimentary knowledge.'
        
        return statement
    
    def get_positive_statement(self, label_name, value_count):    
        """
        Generate a statement based on the value count for positive evaluations.

        Args:
            label_name: The name of the evaluation label.
            value_count: The count of positive evaluations.

        Returns:
            A statement describing the assessment based on the value count.
        """
        if value_count < 50:
            statement = f'Based on the response to the enquiry, the {label_name} evaluation of your oil contains multiple serious shortcomings.'
        elif value_count < 75:
            statement = f'According to the response to the query, the {label_name} evaluation of your oil is generally good. However, there are a few shortcomings that needs be addressed further.'
        elif value_count < 90:
            statement = f'According to the response to the inquery, the {label_name} evaluation of your oil is largely favourable Nonetheless, the aformentioned issues must be considered in to account.'
        else:
            statement = f'According to the response to the query, the {label_name} evaluation of your oil is highly promising. It has a lot of promise in terms of the {self.evalebel.label.adj.lower()}.'

        return statement 
    
    
    def ans_to_the_label(self):
        """
        Get the count of answers related to the evaluation label.

        Returns:
            The count of answers related to the evaluation label.
        """
        filter_kwargs = {
            'evalebel': self.evalebel,
            'evaluator': self.evaluator,
            'question__isnull': False,
            'assesment': False
        }
        values_key = 'evalebel'
        return self.get_statement_count(values_key, **filter_kwargs)
     
    
    def calculate_percentage(self, ans_to_the_lavel):
        """
        Calculate the percentage based on answers related to the evaluation label.

        Args:
            ans_to_the_label: The count of answers related to the evaluation label.

        Returns:
            The percentage calculated based on the given count.
        """
        return (int(ans_to_the_lavel) * 100)/int(self.ans_to_the_label())        

    
    def label_assesment_for_donot_know(self):
        """
        Generate an assessment statement for "don't know" evaluations related to the label.

        Returns:
            An assessment statement based on "don't know" evaluations.
        """
        filter_kwargs = {
            'evalebel' : self.evalebel,  
            'evaluator' : self.evaluator, 
            'question__isnull' : False,
            'dont_know' : 1, 
            'assesment' : False
            }
        values_key = 'evalebel'
        
        dont_know_ans_to_the_lebel = self.get_statement_count(values_key, **filter_kwargs)
        
        dont_know_percent_to_the_label = self.calculate_percentage(dont_know_ans_to_the_lebel)
        
        statement = self.get_dont_know_statement(str(self.evalebel.label.name), int(dont_know_percent_to_the_label))   

        return statement
    
    def label_assesment_for_positive(self):     
        """
        Generate an assessment statement for positive evaluations related to the label.

        Returns:
            An assessment statement based on positive evaluations.
        """  
        filter_kwargs = {
            'evalebel' : self.evalebel,  
            'evaluator' : self.evaluator, 
            'question__isnull' : False,
            'positive' : 1, 
            'assesment' : False
            }
        values_key = 'evalebel'
        
        pos_ans_to_the_lebel = self.get_statement_count(values_key, **filter_kwargs)
        
        positive_percent_to_the_label = self.calculate_percentage(pos_ans_to_the_lebel)
        
        statement = self.get_positive_statement(str(self.evalebel.label.name).lower(), int(positive_percent_to_the_label))    
    
        return statement
    
    def ans_ques(self):   
        """
        Get the count of answerable questions.

        Returns:
            The count of answerable questions.
        """ 
        filter_kwargs = {      
            'evaluator' : self.evaluator, 
            'question__isnull' : False,       
            'assesment' : False
            }
        values_key = 'question'
        
        ans_ques = self.get_statement_count(values_key, **filter_kwargs)   
        
        return ans_ques
    
    def calculate_overall_percent(self, ans):
        """
        Calculate the overall percentage based on the given count.

        Args:
            ans: The count used to calculate the overall percentage.

        Returns:
            The overall percentage calculated based on the given count.
        """
        return (int(ans) * 100)/int(self.ans_ques()) if self.ans_ques() != 0 else 100    

    
    def overall_assesment_for_donot_know(self):
        """
        Generate an overall assessment statement for "don't know" evaluations.

        Returns:
            An overall assessment statement based on "don't know" evaluations.
        """
        filter_kwargs = {      
            'evaluator' : self.evaluator, 
            'question__isnull' : False,
            'dont_know' : 1, 
            'assesment' : False
            }
        values_key = 'question'
        
        dont_know_ans = self.get_statement_count(values_key, **filter_kwargs)       
        
        dont_know_percent = self.calculate_overall_percent(dont_know_ans)
        
        statement = self.get_dont_know_statement('Overall', int(dont_know_percent)) 
        
        return statement
    
    def overall_assesment_for_positive(self):
        """
        Generate an overall assessment statement for positive evaluations.

        Returns:
            An overall assessment statement based on positive evaluations.
        """
        filter_kwargs = {      
            'evaluator' : self.evaluator, 
            'question__isnull' : False,
            'positive' : 1, 
            'assesment' : False
            }
        values_key = 'question'    
        
        pos_ans = self.get_statement_count(values_key, **filter_kwargs)   
        
        positive_percent = self.calculate_overall_percent(pos_ans)
        
        statement = self.get_positive_statement('overall', int(positive_percent))     
        
        return statement


class OilComparision:
    ############## It is nowhere using now but kept for further use if instruction is clear ###################
    def __init__(self, oil, non_answered = None):        
        """
        Initialize an OilComparision instance.

        Args:
            oil: The oil instance for which the comparison is being performed.
            non_answered: A list of non-answered question IDs (optional).
        """
        self.oil = oil       
        
         # Filter active questions that have 4 labels
        if non_answered is not None:            
            self.active_questions = [q for q in Question.objects.filter(id__in = non_answered, is_active=True) if q.have_4labels]   
        else:
            self.active_questions = [q for q in Question.objects.filter(is_active=True) if q.have_4labels]  
         
        # Get standard chart records for the given oil        
        self.oils = StandaredChart.objects.filter(oil = self.oil)
       
    @property   
    def total_active_questions(self): 
        """
        Get the total count of active questions with 4 labels.

        Returns:
            The total count of active questions.
        """
        data = len(self.active_questions)
        return round(data, 2)    
    
    @property
    def total_positive_options(self):        
        '''
        to get positive question based on pisitive option of the oil
        '''
        data = []
        for oil in self.oils:
            try:
                if int(oil.option.positive) == 1:
                    data.append(oil.option)  
            except:
                continue        
        return round(len(data), 2)
    
    @property
    def total_negative_options(self):     
        """
        Get the count of negetive options for the oil.

        Returns:
            The count of negetive options.
        """         
        data = []
        for oil in self.oils:
            try:                             
                if int(oil.option.positive) == 0 and oil.option.dont_know == False:
                    data.append(oil.option)      
            except:
                continue            
        return round(len(data), 2)
    
    @property
    def overview_green(self):
        """
        Calculate the percentage of positive options out of total active questions.

        Returns:
            The percentage of positive options.
        """
        data = (self.total_positive_options/self.total_active_questions)*100    
        return round(data, 2)
        
    @property    
    def overview_red(self):
        """
        Calculate the percentage of negative options out of total active questions.

        Returns:
            The percentage of negative options.
        """ 
        data = (self.total_negative_options/self.total_active_questions)*100    
        return round(data, 2)
    
    @property    
    def overview_grey(self):
        """
        Calculate the percentage of options that are neither positive nor negative out of total active questions.
        
        As overview green and overview red is in parcent so we will deduct from 100 the both to equalized dividation in barchart.
        As each question have no label and have multiple positive value or negative value so sum of labelwise questions result is diferent then actual total question.
        For this reason to get rid of the mismatched result we had to deduct from 100 to get matching report in the barchart.    

        Returns:
            The percentage of such options.
        """
        
        data = 100 - (self.overview_green + self.overview_red)           
        return round(data, 2)
    
    def total_result(self):
        """
        Get the overall results in a dictionary format.
        
        As per writen CSS our fist stacked bar will be green, second bar will be grey and third bar will be red so 
        we will placed the value in the list acordingly. We need to decide label name here so that it will be easy to impleted along with labels as each label has predifiened name.

        Returns:
            A dictionary containing overall results.
        """
        
        record = {
            # green >> grey >> red
            'Overview' : [self.overview_green, self.overview_grey, self.overview_red]
            }
        return record   

    
    def label_wise_positive_option(self, label):    
        """
        Get the count of positive options for a specific label.

        Args:
            label: The label for which positive options are counted.

        Returns:
            The count of positive options for the label.
        """          
        data = self.oils.filter(question__questions__name = label, option__positive = str(1)).count()        
        return round(data, 2)
    
    def label_wise_negative_option(self, label):       
        """
        Get the count of negative options for a specific label.

        Args:
            label: The label for which negative options are counted.

        Returns:
            The count of negative options for the label.
        """       
        data = self.oils.filter(question__questions__name = label, option__positive = str(0), option__dont_know = False).count()       
        return round(data, 2)
    
    def label_wise_result(self):  
        """
        Get label-wise results in a dictionary format.

        Returns:
            A dictionary containing label-wise results.
        """     
        labels = get_all_definedlabel().filter(common_status = False)        
        record_dict = {}
        for label in labels:    
            l_labels = set(label.dlabels.filter(value = 1))
            active_question = len([l.question for l in l_labels if l.question.have_4labels])            
               
            positive_options = round((self.label_wise_positive_option(label)), 2)              
            
            # same as positive
            negative_options = round((self.label_wise_negative_option(label)), 2)      
            
            try:
                green = round((positive_options/active_question)*100, 2)
            except:
                green = 0  
                
            try:
                red = round((negative_options/active_question)*100, 2)
            except:
                red = 0      
                
            try:
                grey = round(100-(green+red),2)
            except:
                grey = 0   
            
            record = {
                # Same as total total result
                # green >> grey >> red
                label.name : [green , grey, red]
            }  
            
            record_dict.update(record)         
               
        return record_dict
    
    
    def picked_labels_dict(self):
        """
        Get the dictionary containing picked labels' results.

        Returns:
            A dictionary containing results for picked labels and the overall result.
        """
        
        label_result = {}    
        label_result.update(self.label_wise_result())
        label_result.update(self.total_result()) 
        return label_result
    
    def packed_labels(self):  
        """
        Create a DataFrame from the picked labels' results.
        From dataframe we will take rows to use in JS's series.

        Returns:
            A DataFrame containing results for picked labels and the overall result.
        """      
        
        df = pd.DataFrame(self.picked_labels_dict())   
        return df  
        


class LabelWiseData:
        
    def __init__(self, evaluator):
        
        """
        Initialize a LabelWiseData instance.

        Args:
            evaluator: The evaluator, which can be from the session or URL.
        """       
        self.evaluator = evaluator   
        
        # Get all active questions with 4 labels 
        self.active_questions = [q for q in get_all_questions().filter(is_active=True) if q.have_4labels]        

        # Get statement data from selected options during answering
        # Exclude assessments and logical strings
        self.eva_label_statement = EvaLebelStatement.objects.filter(
            evaluator = self.evaluator, 
            question__isnull = False, 
            assesment = False
            ).select_related(
                'evalebel', 
                'question', 
                'evaluator'
            )   
    
    @property
    def answered_question_id_list(self):     
        """
        Get a list of unique answered question IDs.

        Returns:
            A list of unique answered question IDs.
        """ 
        data = self.eva_label_statement.values_list('question__id', flat=True)
        return list(set(data))   
    
    @property
    def total_active_questions(self):  
        """
        Get the total count of active questions with 4 labels.

        Returns:
            The total count of active questions.
        """      
        data = len(self.active_questions)         
        return round(data, 2)      
    
    @property
    def answered_percent(self):
        """
        Calculate the percentage of answered questions out of total active questions.

        Returns:
            The percentage of answered questions.
        """
        data = (len(self.answered_question_id_list) / self.total_active_questions * 100)   
        return round(data, 2) 
 
    @property
    def total_positive_answer(self):   
        """
        Get the total count of positive answers.

        Returns:
            The total count of positive answers.
        """    
        data = [s.question.id for s in self.eva_label_statement if s.is_positive]
        return round(len(set(data)), 2)  
          
    @property
    def total_nagetive_answer(self):   
        """
        Get the total count of negative answers.

        Returns:
            The total count of negative answers.
        """     
        try:
            data = set(s.question.id for s in self.eva_label_statement if s.is_negative)
        except:
            data = 0     
        return round(len(data), 2)         
    
    @property
    def overview_green(self):
        """
        Calculate the percentage of positive answers out of total active questions.

        Returns:
            The percentage of positive answers.
        """
        data = (self.total_positive_answer/self.total_active_questions)*100       
        return round(data, 2)
    
    @property
    def overview_red(self):
        """
        Calculate the percentage of negative answers out of total active questions.

        Returns:
            The percentage of negative answers.
        """
        data = (self.total_nagetive_answer/self.total_active_questions)*100      
        return round(data, 2)
    
    @property
    def overview_grey(self):  
        """
        Calculate the percentage of answers that are neither positive nor negative out of total active questions.

        Returns:
            The percentage of such answers.
        """         
        data = 100 - self.overview_green - self.overview_red 
        return round(data, 2)
    
    def total_result(self):
        """
        Get the overall results in a dictionary format.
        
        As per writen CSS our fist stacked bar will be green, second bar will be grey and third bar will be red so 
        we will placed the value in the list acordingly. We need to decide label name here so that it will be easy to 
        impleted along with labels as each label has predifiened name.

        Returns:
            A dictionary containing overall results.
        """
        
        
        '''
        ============================================================
        BELOW COMENTED CODE HAS CONFUSION ON INSTRUCTION SO COMENTED
        ============================================================
        '''
        # try:
        #     std_oil = StdOils.objects.get(select_oil__key = self.evaluator.stdoil_key)
        #     oc = OilComparision(std_oil)
        #     serialized_record = [self.overview_green, self.overview_grey/2, self.overview_red]
            
        #     # # print(serialized_record)
        #     aaaa = list(oc.total_result().values())[0]
        #     # # # print(list(oc.total_result().values())[0])
        #     aa = [(a * (self.overview_grey/2))/100 for a in aaaa]
        #     serialized_record[1:1] = aa
            
        # except:
        #     serialized_record = [self.overview_green, self.overview_grey, self.overview_red]
        '''
        ============================================================
        ABOVE COMENTED CODE HAS CONFUSION ON INSTRUCTION SO COMENTED
        ============================================================
        '''
            
        serialized_record = [self.overview_green, self.overview_grey, self.overview_red]        
        
        record = {            
            'Overview' : serialized_record
            }        
        return record     

    
    def label_wise_positive_answered(self, label):  
        """
        Get the count of positive answers for a specific label.

        Args:
            label: The label for which positive answers are counted.

        Returns:
            The count of positive answers for the label.
        """
        evalebel = label.labels.all()         
        data = self.eva_label_statement.filter(evalebel__in = evalebel, positive = str(1)).count()
        return round(data, 2)    

    
    def label_wise_nagetive_answered(self, label): 
        """
        Get the count of negative answers for a specific label.

        Args:
            label: The label for which negative answers are counted.

        Returns:
            The count of negative answers for the label.
        """
        evalebel = label.labels.all()    
        data = self.eva_label_statement.filter(evalebel__in = evalebel, positive = str(0), dont_know = False).count()      
            
        return round(data, 2)         
   
    
    def label_wise_result(self):      
        """
        Get label-wise results in a dictionary format.

        Returns:
            A dictionary containing label-wise results.
        """ 
        labels = get_all_definedlabel().filter(common_status = False)
        record_dict = {}
        for label in labels:             
            
            l_labels = set(label.dlabels.filter(value = 1))            
            
            active_question = len([l.question for l in l_labels if l.question.is_active and l.question.have_4labels])            
            
            positive_answered = self.label_wise_positive_answered(label)          
            
            negative_answered = self.label_wise_nagetive_answered(label)     
            
            try:
                green = round((positive_answered/active_question)*100, 2)
            except:
                green = 0
            try:
                red = round((negative_answered/active_question)*100, 2)
            except:
                red = 0      
                
            try:
                grey = round(100-(green+red),2)
            except:
                grey = 0   
             
            '''
            ============================================================
            BELOW COMENTED CODE HAS CONFUSION ON INSTRUCTION SO COMENTED
            ============================================================
            '''
            # try:
            #     std_oil = StdOils.objects.get(select_oil__key = self.evaluator.stdoil_key)
            #     oc = OilComparision(std_oil)
            #     serialized_record = [green , grey/2 , red]  
            #     # d = [ v for k, v in oc.label_wise_result() if k == label.name]
            #     # # print(serialized_record)
            #     # print(oc.label_wise_result())
            #     aaaa = [ v for k, v in oc.label_wise_result().items() if k == label.name]
            #     # # # print(list(oc.total_result().values())[0])            
            #     aa = [(a * (grey/2))/100 for a in aaaa[0]]
                
            #     serialized_record[1:1] = aa                
                
            # except Exception as e:                
            #     serialized_record = [green , grey, red]  
                
            '''
            ============================================================
            ABOVE COMENTED CODE HAS CONFUSION ON INSTRUCTION SO COMENTED
            ============================================================
            '''
            serialized_record = [green , grey, red]  
            
            record = {                
                #green>>grey>>red
                label.name: serialized_record
            }        
            record_dict.update(record)     
            
               
        return record_dict
    
    def picked_labels_dict(self):
        """
        Get the dictionary containing picked labels' results.

        Returns:
            A dictionary containing results for picked labels and the overall result.
        """
        label_result = {}    
        label_result.update(self.label_wise_result())
        label_result.update(self.total_result())        
        return label_result
    
    def packed_labels(self):
        """
        Create a DataFrame from the picked labels' results.
        From dataframe we will take rows to use in JS's series.

        Returns:
            A DataFrame containing results for picked labels and the overall result.
        """   
        
        df = pd.DataFrame(self.picked_labels_dict())   
        return df
    
    def label_data_history(self):
        """
        Get historical label data.

        Returns:
            A list of dictionaries containing historical label data.
        """
        data = LabelDataHistory.objects.filter(evaluator = self.evaluator) 
        result_dict=[]
        for d in data:
            item_dict = {
                (d.created).strftime('%d-%m-%Y') : eval(d.items)
                }
            result_dict.append(item_dict)
        date_wise_df_list = []
        for rd in result_dict:
            for key, values in rd.items():
                vf = pd.DataFrame(values)
                vf_label = vf.columns.values.tolist()
                vf_data = vf.values.tolist()
                date_wise_df = {
                    key : [vf_label, vf_data]
                }
                date_wise_df_list.append(date_wise_df)       
        
        return date_wise_df_list    
        
    
def nreport_context(request, slug): 
    """
    Generate a comprehensive PDF report context for a given evaluator.

    Args:
        request: The HTTP request object.
        slug: The unique identifier (slug) of the evaluator.

    Returns:
        A dictionary containing all the data required for generating the PDF report.
    """ 
    
    # Clear the evaluator session variable to allow editing the report.
    request.session['evaluator'] = ''
    
    # Clear unnecessary session variables for completed reports.
    try:        
        del request.session['question']
        del request.session['total_question']            
    except KeyError:
        pass

    # Try to retrieve the evaluator report using the provided slug.
    try:  
        get_report = Evaluator.objects.get(slug = slug)
    except:
        messages.warning(request, 'No report found!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    # Create a LabelWiseData instance for the evaluator.
    label_data = LabelWiseData(get_report)
    
    # Generate data for PDF report.
    df = label_data.packed_labels() 
    dfh = label_data.label_data_history()    
    
    # Get evaluation data for the evaluator.
    evaluation = Evaluation.objects.filter(evaluator=get_report).order_by('id').select_related('question', 'option')
  
    # Get evaluator labels and statements.
    eva_label = EvaLabel.objects.filter(evaluator=get_report).order_by('sort_order').prefetch_related('elabelstatement')
    eva_statment = EvaLebelStatement.objects.filter(evalebel__evaluator=get_report).order_by('pk').select_related('evalebel', 'question', 'evaluator')
    
    # Get ordered next activities for the evaluator.
    next_activities = NextActivities.objects.prefetch_related('related_questions').all().order_by('priority')    
    
    # Get the common label, which is "executive summary."  
    common_label = eva_label.get(label__common_status = True)
    
    # Delete any previous records for the current report related to the common label.
    try:
        EvaLebelStatement.objects.filter(evalebel = common_label, evaluator =  get_report, next_activity = True).delete()        
    except:
        pass   
    
    '''
    ========
    part of next activitis started
    ========
    '''
    # Calculate the percentage of answered questions for this report.
    questions_of_report = set()   
    for es in eva_statment:    
        # Exclude "don't know" questions.
        if es.question and not es.dont_know:            
            questions_of_report.add(es.question)  
             
    # Initialize a list to store active next activities.
    na_ac = []
    
    # Iterate through next activities and calculate related and compulsory question percentages.
    for na in next_activities:         
       
        related_questions = set(na.related_questions.all())
        compulsory_questions = set(na.compulsory_questions.all())
        
        rel_ques_pecent_in_report = round(len(questions_of_report.intersection(related_questions))/len(related_questions)*100, 2)
        com_ques_percent_in_report = round(len(questions_of_report.intersection(compulsory_questions))/len(compulsory_questions)*100, 2)        
        
        try:  
            # Update existing EvaluatorActivities with new percentages if they exist.     
            eva_ac = EvaluatorActivities.objects.get(evaluator=get_report, next_activity=na)            
            eva_ac.related_percent = rel_ques_pecent_in_report
            eva_ac.compulsory_percent = com_ques_percent_in_report 
            eva_ac.save()            
        except:  
            # Create a new EvaluatorActivities record if it doesn't exist.                 
            eva_ac = EvaluatorActivities.objects.create(evaluator=get_report, next_activity=na, related_percent = rel_ques_pecent_in_report, compulsory_percent = com_ques_percent_in_report ) 
        
        # Determine if the next activity is active (completed, not completed, not started, or unknown).
        if int(eva_ac.related_percent) >= int(na.related_percent) and int(eva_ac.compulsory_percent) >= int(na.compulsory_percent):            
            setattr(na, 'is_active', 'Completed')  
        elif int(eva_ac.related_percent) < int(na.related_percent) and int(eva_ac.related_percent) > 0 and int(eva_ac.compulsory_percent) >= int(na.compulsory_percent):
            setattr(na, 'is_active', 'Not Completed')  
        elif int(eva_ac.related_percent) <= 0:  
            #if 0 we will consider not started becoz if it is touched any percentage can be set.          
            setattr(na, 'is_active', 'Not Started')                         
        else:
            setattr(na, 'is_active', 'Unknown for this report')  
            
         # Append non-completed next activities to the list (up to a maximum of 5). 
        if na.is_active != 'Completed':  
            if len(na_ac) <= 5:
                na_ac.append(na)
            else:
                break
        else:
            continue

    '''
    ========
    part of next activitis end
    ========
    '''  
    # Prepare the report context dictionary.
    context = {
        'evaluation': evaluation,
        'current_evaluator': get_report,
        'eva_label': eva_label,
        'eva_statment': eva_statment,
        'next_activities' : next_activities,
        'site_name': get_current_site(request).name,
        'item_label' : df.columns.values.tolist(),
        'item_seris' : df.values.tolist(),
        'na_ac' : na_ac,
        'dfh' : dfh
    }

    return context


def get_sugested_questions(request):
    """
    Retrieve suggested questions submitted by the current user.

    Args:
        request: The HTTP request object containing the user information.

    Returns:
        QuerySet: A QuerySet of suggested questions submitted by the user.
    """
    # Filter Suggestions objects by the current user, type 'question', and no associated question.
    sugested_questions = Suggestions.objects.filter(sugested_by = request.user, su_type = 'question', question = None) 
       
    return sugested_questions


def get_picked_na(question):
    """
    Retrieve active next activities that involve a specific question.

    Args:
        question: The Question object to check for inclusion in next activities.

    Returns:
        list: A list of active NextActivities objects that involve the specified question.
    """
    
    # Retrieve all active NextActivities.
    next_activities = NextActivities.objects.filter(is_active = True)
    
    # Initialize an empty list to store picked next activities.
    picked_na = []
    
    # Iterate through active next activities and check if the question is involved.
    for na in next_activities:
        if question in na.answering_questions:
            picked_na.append(na)
    return picked_na
        

from django.contrib.sites.models import Site
def build_full_url(path):
    """
    Build a full URL by appending a path to the domain of the current site.

    Args:
        path (str): The path or URL component to append.

    Returns:
        str: The full URL.
    """
    current_site = Site.objects.get_current()
    domain = current_site.domain

    # Check if the domain already contains 'http://' or 'https://'
    if not domain.startswith('http://') and not domain.startswith('https://'):
        protocol = 'https://' if current_site.domain.startswith('www.') else 'http://'
    else:
        protocol = ''

    # Ensure that the path starts with a forward slash
    if not path.startswith('/'):
        path = '/' + path

    # Construct the full URL
    full_url = f"{protocol}{domain}{path}"

    return full_url