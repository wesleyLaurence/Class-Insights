# import librarys
import pandas as pd
import os 
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# Pandas settings
# display untruncated data from pandas
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', 999)
pd.set_option('display.max_rows', 100)


class attendance(object):
    
    def __init__(self):
        
        self.home_directory =  Path(str(pathlib.Path(__file__).parent.absolute()))
        
        # retrieve strings of file names from your directory
        entries = os.listdir(self.home_directory+'datasets')
        
        # ROSTER    
        for filename in entries:
            # load student roster
            if 'roster' in filename.lower():
                roster = pd.read_excel(self.home_directory+'datasets\\'+filename)
                student_list_main = list(roster['name_365'])
            else:
                pass
            

        # this searches your directory for xlsx files (projects and assignments from Microsoft Froms Excel sheets) 
        student_submissions = []

        # Sort Excel files
        for filename in entries:           
            # load student attendance
            if 'attendance' in filename.lower():
                # import data from excel file
                attendance = pd.read_excel(self.home_directory+'datasets/'+filename)
                # remove extraneous columns
                attendance = attendance[['Start time','Name']].copy()
                # extract date from timestamp and add to new column in attendance dataframe
                attendance['Date'] = [attendance_timestamp.date() for attendance_timestamp in attendance['Start time']]
                # set columns order
                attendance = attendance[['Name','Start time','Date']]
                # create master attendance dataframe
                attendance_df = roster[['name_365','name_focus','class','grade','gender']].copy()
            
            # load student submissions
            elif 'assignment' in filename.lower() or 'project' in filename.lower() or 'quiz' in filename.lower() or 'test' in filename.lower():              
                # import data from excel file
                assignment = pd.read_excel(self.home_directory+'datasets/'+filename)
                # remove extraneous columns
                assignment = assignment[['Start time','Name']].copy()    
                # extract date from timestamp and add to new column in attendance dataframe
                assignment['Date'] = [assignment_timestamp.date() for assignment_timestamp in assignment['Start time']]      
                # set columns order
                assignment = assignment[['Name','Start time','Date']]
                # add data frame to student_submissions list             
                student_submissions.append(assignment)
            
            else:
                pass  
        
        
        ### Check for attendance

        # for each unique date in sign in history
        unique_dates_checkin = list(attendance['Date'].unique())
        filtered_dates = []

        # for each date in daily check in history
        for unique_date in unique_dates_checkin:

            # return all attendance submissions for single day
            single_day_attendance = attendance[attendance['Date'] == unique_date].copy()

            # classify students as present or absent
            attendance_cache = []
            for student in student_list_main:
                if student in list(single_day_attendance['Name']):
                    attendance_cache.append('P')
                else:
                    attendance_cache.append('A')
             
            # filter out weekends
            num_absent = pd.Series(attendance_cache).value_counts()[0]
            if num_absent > 70:
                pass
            else:
                filtered_dates.append(unique_date)
                # add new data to master attendance dataframe
                attendance_df.loc[:,str(unique_date)] = attendance_cache


        unique_dates_checkin = filtered_dates
        ### Check for assignment completion
        
        # create master attendance dataframe
        assignment_df = roster[['name_365','name_focus','class','grade','gender']].copy() 

        
        # for each submission (assignment, quiz etc)
        for student_submission in student_submissions:
        
            unique_dates_assignments = list(student_submission['Date'].unique())
            for unique_date in unique_dates_assignments:

                # return all attendance submissions for single day
                single_day_assignment = assignment[assignment['Date'] == unique_date].copy()
                assign_names = list(single_day_assignment['Name'])

                # for each student who did submit their assignment on the current unique_date
                for student_name in assign_names:
                    student_num = int(list(student_list_main).index(student_name))
                    attendance_df.loc[student_num,str(unique_date)] = 'P'

        attendance_df = attendance_df.dropna(axis=1)
        self.attendance_factor = {'A'}
        attendance_df['total_absent'] = attendance_df.isin(self.attendance_factor).sum(1)
        attendance_df.index = attendance_df['name_focus']
        attendance_df.drop(['name_365','name_focus'],axis=1,inplace=True)
        
        self.main = attendance_df
        
        # does a value count for every day in the checkin
        attendance_summary = pd.DataFrame([])
        for date_value in unique_dates_checkin:
            day = attendance_df[str(date_value)].value_counts()
            attendance_summary[str(date_value)] = day
        attendance_summary.index = ['Present','Absent']
        self.summary = attendance_summary.T  
        self.total_absent = attendance_df.sort_values(by='total_absent',ascending=False)
        self.total_absent = self.total_absent[['class','grade','total_absent']]
        
        
    
    def dashboard(self):
        
        plt.style.use('seaborn-bright')
        # Total Absences
        total_Ps = self.summary.T.loc['Absent']
        #fig1 = plt.figure(1) 
        plt.title('Total Absences')
        
        xtix_list = list(self.summary.T.columns)
        plt.xlabel('Date')
        plt.ylabel('# of Students')
        plt.xticks([0,len(xtix_list)-1],[xtix_list[0],xtix_list[-1]], visible=True, rotation="horizontal")
        plt.plot(total_Ps, alpha=0.8)
        plt.show()
        
        # see absence distribution
        x = list(self.total_absent['total_absent'].value_counts().sort_index().index)
        energy = list(self.total_absent['total_absent'].value_counts().sort_index())

        x_pos = [i for i, _ in enumerate(x)]
        plt.title('Total Absence Distribution')
        plt.bar(x_pos, energy, alpha=0.8)
        plt.xlabel("Total Absences")
        plt.ylabel("# of Students")

        plt.show()
        
        ### AVG by gender

        female = self.main[self.main['gender']=='F'].copy()
        female['total_absence'] = female.isin(self.attendance_factor).sum(1)
        avg_absences_female = female['total_absence'].mean()

        male = self.main[self.main['gender']=='M'].copy()
        male['total_absence'] = male.isin(self.attendance_factor).sum(1)
        avg_absences_male = male['total_absence'].mean()

        ### AVG by grade level

        seniors = self.main[self.main['grade']==12].copy()
        seniors['total_absence'] = seniors.isin(self.attendance_factor).sum(1)
        avg_absences_seniors = seniors['total_absence'].mean()

        juniors = self.main[self.main['grade']==11].copy()
        juniors['total_absence'] = juniors.isin(self.attendance_factor).sum(1)
        avg_absences_juniors = juniors['total_absence'].mean()

        sophomores = self.main[self.main['grade']==10].copy()
        sophomores['total_absence'] = sophomores.isin(self.attendance_factor).sum(1)
        avg_absences_sophomores = sophomores['total_absence'].mean()

        ### AVG by class period
        A3_class = self.main[self.main['class']=='A3'].copy()
        A3_class['total_absence'] = A3_class.isin(self.attendance_factor).sum(1)
        avg_absences_A3 = A3_class['total_absence'].mean()

        A4_class = self.main[self.main['class']=='A4'].copy()
        A4_class['total_absence'] = A4_class.isin(self.attendance_factor).sum(1)
        avg_absences_A4 = A4_class['total_absence'].mean()

        B7_class = self.main[self.main['class']=='B7'].copy()
        B7_class['total_absence'] = B7_class.isin(self.attendance_factor).sum(1)
        avg_absences_B7 = B7_class['total_absence'].mean()

        B8_class = self.main[self.main['class']=='B8'].copy()
        B8_class['total_absence'] = B8_class.isin(self.attendance_factor).sum(1)
        avg_absences_B8 = B8_class['total_absence'].mean()

        # summary stats
        gender_absence_stats = pd.DataFrame(pd.Series({'Female':avg_absences_female,'Male': avg_absences_male}),columns=['AVG Total Absence'])
        grade_absence_stats = pd.DataFrame(pd.Series({'Senior': avg_absences_seniors, 'Junior':avg_absences_juniors, 'Sophomore':avg_absences_sophomores}),columns=['AVG Total Absence'])
        class_absence_stats = pd.DataFrame(pd.Series({'A3':avg_absences_A3, 'A4':avg_absences_A4, 'B7':avg_absences_B7, 'B8':avg_absences_B8}),columns=['AVG Total Absence'])
        
        
        objects = ('Sophomore', 'Junior', 'Senior')
        y_pos = np.arange(len(objects))

        # get class info from class_absence_stats dataframe
        performance = [grade_absence_stats.iloc[2,0],  grade_absence_stats.iloc[0,0],  grade_absence_stats.iloc[1,0]]
        #fig2 = plt.figure(2) 
        plt.bar(y_pos, performance, align='center', alpha=0.8)
        plt.xticks(y_pos, objects)
        plt.ylabel('AVG # of Absences')
        plt.xlabel('Grade Level')
        plt.title('AVG Absences by Grade Level')
        plt.show()
        
        
        objects = ('A3', 'A4', 'B7', 'B8')
        y_pos = np.arange(len(objects))

        # get class info from class_absence_stats dataframe
        performance = [class_absence_stats.iloc[0,0],  class_absence_stats.iloc[1,0],  class_absence_stats.iloc[2,0],  class_absence_stats.iloc[3,0]]
        #fig3 = plt.figure(3) 
        plt.bar(y_pos, performance, align='center', alpha=0.8)
        plt.xticks(y_pos, objects)
        plt.ylabel('AVG # of Absences')
        plt.xlabel('Class Period')
        plt.title('AVG Absences by Class Period')
        plt.show()
        
        
        
        objects = ('Female', 'Male')
        y_pos = np.arange(len(objects))

        # get class info from class_absence_stats dataframe
        performance = [gender_absence_stats.iloc[0,0],  gender_absence_stats.iloc[1,0]]
        #fig4 = plt.figure(4) 
        plt.bar(y_pos, performance, align='center', alpha=0.8)
        plt.xticks(y_pos, objects)
        plt.ylabel('AVG # of Absences')
        plt.xlabel('Gender')
        plt.title('AVG Absences by Gender')
        plt.show()
        
        
    def absent(self,date1,date2):
        
        df = self.main[['class',date1,date2]].copy()
        df = df[(df[date1]=='A') & (df[date2]=='A')]
        
        return df
        
        
class grades(object):

    def __init__(self):
        
        self.home_directory =  Path(str(pathlib.Path(__file__).parent.absolute()))

        # retrieve strings of file names from your directory
        entries = os.listdir(self.home_directory+'\\datasets')
        entries.sort()

        #this searches your directory for xlsx files (projects and assignments from Microsoft Froms Excel sheets) 

        # each item in this list is a dataframe of submissions
        student_submissions = []

        # each item is a string, the title of the submission
        submission_names = []

        # Sort Excel files
        for filename in entries:           

            # ROSTER 
            if 'roster' in filename.lower():
                roster = pd.read_excel(self.home_directory+'datasets/'+filename,encoding='latin1', index_col='name_365')
                main_name_list = list(roster.index)

            # load student submissions
            elif ('assignment' in filename.lower()) or ('project' in filename.lower()) or ('quiz' in filename.lower()) or ('test' in filename.lower()):
                submission_names.append(filename)
                # import data from excel file
                assignment = pd.read_excel(self.home_directory+'datasets/'+filename)

                # if graded assignment...
                if 'Total points' in list(assignment.columns):
                    # remove extraneous columns
                    assignment = assignment[['Start time','Name','Total points']].copy()    
                    # extract date from timestamp and add to new column in attendance dataframe
                    assignment['Date'] = [assignment_timestamp.date() for assignment_timestamp in assignment['Start time']]      
                    # set columns order
                    assignment = assignment[['Name','Total points','Start time','Date']]
                    # add data frame to student_submissions list             
                    student_submissions.append(assignment)

                # if completion assignment...
                else:
                    # remove extraneous columns
                    assignment = assignment[['Start time','Name']].copy()    
                    # extract date from timestamp and add to new column in attendance dataframe
                    assignment['Date'] = [assignment_timestamp.date() for assignment_timestamp in assignment['Start time']]      
                    # set columns order
                    assignment = assignment[['Name','Start time','Date']]
                    # add data frame to student_submissions list             
                    student_submissions.append(assignment)      
            else:
                pass



        # container for cleansed assignment/project names. 
        short_file_names = []

        # Remove spaces, make lowercase and delete excess title info for each item in file_names list      
        for file in submission_names:  
            new_file =''
            for character in file:
                if character.isdigit():
                    new_file = new_file + str(character)
                    break
                else:
                    new_file = new_file + character
                    pass
            new_file=new_file.lower()
            new_file=new_file.replace(' ','_')
            short_file_names.append(new_file)      




        gradebook = roster[['name_focus','class']].copy()

        file_num=0
        for submission in student_submissions:

            submission_title = short_file_names[file_num]

            # if graded assignment...
            if 'Total points' in list(submission.columns):

                # create new column in dataframe
                gradebook[submission_title] = int(0)

                names = submission['Name']
                grade_values = submission['Total points']

                i=0
                for student_name in names:
                    gradebook.loc[student_name, submission_title] = int(grade_values[i])
                    i+=1

            # if completion assignment...
            else:
                names = submission['Name']

                i=0
                for student_name in names:
                    gradebook.loc[student_name, submission_title] = int(100)
                    i+=1

            file_num+=1

        gradebook.reset_index(inplace=True)
        gradebook.drop('name_365',axis=1,inplace=True)
        gradebook.set_index('name_focus',inplace=True)
        
        # scale total points from 12 to 100
        gradebook.loc[:,'quiz_1'] = (np.round(gradebook['quiz_1']/12,2)*100).astype(int)

        # replace nan values with 0
        gradebook.fillna(0,inplace=True)

        # remove students who dropped class
        gradebook = gradebook[pd.notnull(gradebook.index)]
        
        
        # create attendance score for each student
        attendance_score = 100-(attendance().main['total_absent'] / 8)*100

        # create averages for each classwork category
        assignment_avgs = (gradebook['assignment_6'] + gradebook['assignment_7'] + gradebook['assignment_8']) / 3
        quiz_avgs = (gradebook['quiz_1'] + gradebook['quiz_2']) / 2
        project_avgs = gradebook['project_6']

        # create total grade score for each student
        grades_score = assignment_avgs*.25 + quiz_avgs*.25 + project_avgs*.5

        # combine attendance and grades into student_rank
        student_rank = attendance_score*.4 + grades_score*.6
        gradebook['average'] = list(grades_score)

        # sort with highest ranked student at top
        student_rank.sort_values(ascending=False,inplace=True)
        self.scores = pd.DataFrame(student_rank,columns=['student_score'])
        
        self.low_grades = pd.DataFrame(gradebook['average'].sort_values(ascending=True)[:20])
        
        self.gradebook = gradebook
        
    
    def completion(self):
        
        # completion percentages
        complete = []
        incomplete = []
        
        for submission_title in list(self.gradebook.columns[1:-1]):
            
            for item in (self.gradebook[submission_title]):
                if item == 0:
                    incomplete.append(1)
                else:
                    complete.append(1)

        objects = ('Complete', 'Incomplete')
        y_pos = np.arange(len(objects))

        # get class info from class_absence_stats dataframe
        performance = [len(complete),len(incomplete)]
        #fig2 = plt.figure(2) 
        plt.bar(y_pos, performance, align='center', alpha=0.8)
        plt.xticks(y_pos, objects)
        plt.ylabel('# of submissions')
        plt.xlabel('Submission Status')
        plt.title('Total Completion')
        plt.show()