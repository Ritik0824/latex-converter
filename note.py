import re
import pandas as pd

# Helper functions
def clean_question_text(raw_question):
    raw_question = str(raw_question)
    raw_question = raw_question.strip()

    # Extract the content within \textbf{} and replace LaTeX newlines with HTML <br>
    # Here, first ensure that the regex finds something to avoid NoneType errors
    textbf_content = re.search(r'\\textbf\{(.+?)\}', raw_question)
    if textbf_content:
        formatted_textbf = re.sub(r'\\\\', '<br>', textbf_content.group(1))
        formatted_textbf = f'<strong>{formatted_textbf}</strong>'
    else:
        formatted_textbf = ""

    # Remove all LaTeX commands, assuming they don't overlap with \textbf{} handling above
    clean_text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', raw_question)
    # Remove single backslashes that might be left over, except for new lines replaced by <br>
    clean_text = re.sub(r'\\(?!<br>)', '', clean_text)
    clean_text = re.sub(r'(?<!\{)[}]', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    clean_text = re.sub(r'^\d+\.\s*', '', clean_text)

    # Replace the extracted \textbf{} content back into the cleaned text if it was found
    if formatted_textbf:
        # You might need to adjust this to place the formatted text at a specific position
        clean_text = formatted_textbf + " " + clean_text

    return clean_text

def clean_options(raw_options):
    cleaned_options = []
    raw_options = str(raw_options)
    options_list = raw_options.split('% Option')
    for option in options_list:
        match = re.search(r'\((.*?)\)\s*\\\(.*?\\\)', option)
        if match:
            original_label = match.group(1)
            latex_expr = re.search(r'\\\(.*?\\\)', option).group(0)
            #latex_expr = re.sub(r'\\\\', '<br>', latex_expr.group(0))
            latex_expr_cleaned = latex_expr.replace(r'\\\\', '<br>')
            cleaned_option = f'{latex_expr_cleaned}'
            cleaned_options.append(cleaned_option)
    return cleaned_options

def create_option_columns_with_labels(cleaned_options):
    # Create a dictionary to hold the columns dynamically
    options_dict = {}

    for i, option in enumerate(cleaned_options, start=1):
        # Assign Option 1, Option 2, etc., based on position
        column_name = f"Option_{i}_en"  # Dynamic column naming
        options_dict[column_name] = option

    # Convert the dictionary into a DataFrame with one row
    options_df = pd.DataFrame([options_dict])
    return options_df


def clean_correct_answer(raw_answer):
    raw_answer = raw_answer.strip()
    raw_answer = str(raw_answer)
    match = re.search(r'\\textbf{Correct Answer:} (.*?\\\(.*?\\\))', raw_answer)
    if match:
        answer_text = match.group(1)
        option_match = re.search(r'\((.*?)\)', answer_text)
        latex_expr_match = re.search(r'\\\(.*?\\\)', answer_text)
        if option_match and latex_expr_match:
            option = option_match.group(0)
            latex_expr = latex_expr_match.group(0)
            latex_expr = latex_expr.replace(r'\\\\', '<br>')
            #latex_expr_cleaned = latex_expr.replace('\\(', '').replace('\\)', '').replace("\\", "")
            final_answer = f'{option} {latex_expr}'
            return final_answer.strip()
    return None

def clean_solution(raw_solution):
    raw_solution = str(raw_solution)
    raw_solution = raw_solution.strip()
    cleaned_solution = re.sub(r'.*?% Solution\s*\\noindent\s*\\textbf{Solution:}', '', raw_solution)
    cleaned_solution = re.sub(r'\n', '', cleaned_solution)
    cleaned_solution = re.sub(r'\s+', ' ', cleaned_solution).strip()
    cleaned_solution = cleaned_solution.replace(r'\\\\', '<br>')
    return cleaned_solution

def clean_quicktip(raw_quicktip):
    raw_quicktip = str(raw_quicktip)
    cleaned_quicktip = re.sub(r'^% Quick Tip\s*', '', raw_quicktip)
    cleaned_quicktip = re.sub(r'.*?{quicktipbox}\s*', '', cleaned_quicktip)
    cleaned_quicktip = re.sub(r'\\end{quicktipbox}.*', '', cleaned_quicktip)
    #tip = re.sub(r'\\', '', cleaned_quicktip)
    cleaned_quicktip = re.sub(r'\s+', ' ', cleaned_quicktip).strip()
    cleaned_quicktip = cleaned_quicktip.replace(r'\\\\', '<br>')
    return cleaned_quicktip


# Main Function
# Main function
# Main function
# Main function
def extract_latex_to_dataframe(latex_code):
    # Define regex patterns
    question_text_pattern = r'% Question text(.*?)% Option'
    option_pattern = r'(% Option.*?)(?=% Correct Answer)'
    correct_answer_pattern = r'% Correct Answer(.*?)% Solution'
    solution_pattern = r'(% Solution.*?)(?=% Quick Tip)'
    quick_tip_pattern = r'(% Quick Tip.*?)(?=\\end\{quicktipbox\})'

    # Extract sections using regex
    question_texts = re.findall(question_text_pattern, latex_code, re.DOTALL)
    options = re.findall(option_pattern, latex_code, re.DOTALL)
    correct_answers = re.findall(correct_answer_pattern, latex_code, re.DOTALL)
    solutions = re.findall(solution_pattern, latex_code, re.DOTALL)
    quick_tips = re.findall(quick_tip_pattern, latex_code, re.DOTALL)


    # Create a DataFrame
    data = []

    for i, raw_question in enumerate(question_texts):
        question_text = clean_question_text(raw_question)

        # Process options
        raw_options = options[i] if i < len(options) else None
        cleaned_options = clean_options(raw_options) if raw_options else []
        options_df = create_option_columns_with_labels(cleaned_options)

        # Process correct answer
        raw_correct_answer = correct_answers[i] if i < len(correct_answers) else None
        correct_answer = clean_correct_answer(raw_correct_answer) if raw_correct_answer else None

        # Process solution
        raw_solution = solutions[i] if i < len(solutions) else None
        solution = clean_solution(raw_solution) if raw_solution else None

        # Process quick tip
        raw_quick_tip = quick_tips[i] if i < len(quick_tips) else None
        quick_tip = clean_quicktip(raw_quick_tip) if raw_quick_tip else None

        # Combine all into a single row
        '''
        row = {
            'S.no': i + 1,
            'Question text': question_text,
            'Correct Answer': correct_answer,
            'Solution': solution,
            'Quick Tip': quick_tip,
        }

        # Add options to the row
        for col in options_df.columns:
            row[col] = options_df[col].iloc[0]'''
        row = {
            'S.no': i + 1,
            'Question text': question_text,
        }

        # Add options to the row
        for col in options_df.columns:
            row[col] = options_df[col].iloc[0]

        # Add the remaining columns in the desired order
        row['Correct Answer'] = correct_answer
        row['Solution'] = solution
        row['Quick Tip'] = quick_tip
        data.append(row)

    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    return df
    

def process_latex_input(latex_input):
    """
    A wrapper function to process LaTeX input safely.
    """
    try:
        df = extract_latex_to_dataframe(latex_input)
        if df.empty:
            return pd.DataFrame()  # Ensure always returning a DataFrame
    except Exception as e:
        print(f"Error processing LaTeX input: {e}")
        return pd.DataFrame()
    return df
