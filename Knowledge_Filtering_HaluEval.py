from helpers import *
from datasets import load_dataset
from sklearn.metrics import f1_score
import pandas as pd
from datetime import datetime

# Retrieve the HaluEval dataset from Hugginface
ds = load_dataset("pminervini/HaluEval", "summarization")
dataset = ds['data']
df = dataset.to_pandas()

# Remove the first three rows used for fewshot prompting
df = df.iloc[3:]

# TODO: Set parameters for the number of rows to analyse
n = 25

# Ignore the rows already analyzed
df = df.iloc[9000:]

# Initialize lists to store true labels and predicted labels for F1 score calculation
true_labels = []
baseline_preds = []
phi3_knowledge_summary_optimized_preds = []
gpt4o_mini_knowledge_summary_optimized_preds = []
gpt4o_knowledge_summary_optimized_preds = []

for i in range(n):
    row = df.iloc[i]
    document = row['document']
    right_summary = row['right_summary']
    hallucinated_summary = row['hallucinated_summary']
    
    results_per_iteration = pd.DataFrame(columns=[
    'Row', 'Document', 'Right Summary', 'Hallucinated Summary', 
    'True Label', 'Baseline Prediction', 'Phi3 Knowledge Optimized Prediction', 
    'GPT4o Mini Knowledge Optimized Prediction', 'GPT4o Knowledge Optimized Prediction',
    'Phi3 Filtered Document', 'GPT4o Mini Filtered Document', 'GPT4o Filtered Document'
    ])

    print("-" * 100)
    print("ANALYZING ROW", i+1, "OF", n, "...")
    print("-" * 100)

    # Print the values of the selected row
    print("Document:", document)
    print("Right Summary:", right_summary)
    print("Hallucinated Summary:", hallucinated_summary)
    print("-" * 100)
    
    # Run the analysis for right summary
    print("Running the process for a non-hallucinated summary")
    true_labels.append(0)
    
    baseline_pred = baseline(document, right_summary)
    baseline_preds.append(baseline_pred)
    
    (phi3_knowledge_summary_optimized_pred, filtered_document_phi3) = knowledge_filtering("phi3", document, right_summary)
    phi3_knowledge_summary_optimized_preds.append(phi3_knowledge_summary_optimized_pred)
        
    (gpt4o_mini_knowledge_summary_optimized_pred, filtered_document_gpt4o_mini) = knowledge_filtering("gpt4o_mini", document, right_summary)
    gpt4o_mini_knowledge_summary_optimized_preds.append(gpt4o_mini_knowledge_summary_optimized_pred)
    
    (gpt4o_knowledge_summary_optimized_pred, filtered_document_gpt4o) = knowledge_filtering("gpt4o", document, right_summary)
    gpt4o_knowledge_summary_optimized_preds.append(gpt4o_knowledge_summary_optimized_pred)
    
    # Save the results of the current iteration for the true summary
    results_per_iteration = pd.concat([results_per_iteration, pd.DataFrame([{
        'Row': i+1, 
        'Document': document, 
        'Right Summary': right_summary, 
        'Hallucinated Summary': '',
        'True Label': 0,
        'Baseline Prediction': baseline_pred,
        'Phi3 Knowledge Optimized Prediction': phi3_knowledge_summary_optimized_pred,
        'Phi3 Filtered Document': filtered_document_phi3,
        'GPT4o Mini Knowledge Optimized Prediction': gpt4o_mini_knowledge_summary_optimized_pred,
        'GPT4o Mini Filtered Document': filtered_document_gpt4o_mini,
        'GPT4o Knowledge Optimized Prediction': gpt4o_knowledge_summary_optimized_pred,
        'GPT4o Filtered Document': filtered_document_gpt4o,
    }])], ignore_index=True)
    
    # Run the analysis for hallucinated summary
    print("-" * 100)
    print("Running the process for a hallucinated summary")
    true_labels.append(1) 
    
    baseline_pred = baseline(document, hallucinated_summary)
    baseline_preds.append(baseline_pred)
    
    (phi3_knowledge_summary_optimized_pred, filtered_document_phi3) = knowledge_filtering("phi3", document, hallucinated_summary)
    phi3_knowledge_summary_optimized_preds.append(phi3_knowledge_summary_optimized_pred)
        
    (gpt4o_mini_knowledge_summary_optimized_pred, filtered_document_gpt4o_mini) = knowledge_filtering("gpt4o_mini", document, hallucinated_summary)
    gpt4o_mini_knowledge_summary_optimized_preds.append(gpt4o_mini_knowledge_summary_optimized_pred)
    
    (gpt4o_knowledge_summary_optimized_pred, filtered_document_gpt4o) = knowledge_filtering("gpt4o", document, hallucinated_summary)
    gpt4o_knowledge_summary_optimized_preds.append(gpt4o_knowledge_summary_optimized_pred)
    
    # Save the results of the current iteration for the hallucinated summary
    results_per_iteration = pd.concat([results_per_iteration, pd.DataFrame([{
        'Row': i+1, 
        'Document': document, 
        'Right Summary': '',
        'Hallucinated Summary': hallucinated_summary,
        'True Label': 1,
        'Baseline Prediction': baseline_pred,
        'Phi3 Knowledge Optimized Prediction': phi3_knowledge_summary_optimized_pred,
        'Phi3 Filtered Document': filtered_document_phi3,
        'GPT4o Mini Knowledge Optimized Prediction': gpt4o_mini_knowledge_summary_optimized_pred,
        'GPT4o Mini Filtered Document': filtered_document_gpt4o_mini,
        'GPT4o Knowledge Optimized Prediction': gpt4o_knowledge_summary_optimized_pred,
        'GPT4o Filtered Document': filtered_document_gpt4o
    }])], ignore_index=True)
    
    # Save the current iteration results to a CSV file
    results_per_iteration.to_csv("Knowledge_Filtering.csv", mode='a', header=not pd.io.common.file_exists("Knowledge_Filtering.csv"), index=False)


print("-" * 100)
print(f"Results after {n} iterations:\n")

# Calculate and print the accuracies
accuracies = {}

accuracies['baseline_TNR'] = sum([1 for i in range(0, 2*n, 2) if baseline_preds[i] == 0]) / n
accuracies['baseline_TPR'] = sum([1 for i in range(1, 2*n, 2) if baseline_preds[i] == 1]) / n

accuracies['phi3_knowledge_summary_optimized_TNR'] = sum([1 for i in range(0, 2*n, 2) if phi3_knowledge_summary_optimized_preds[i] == 0]) / n
accuracies['phi3_knowledge_summary_optimized_TPR'] = sum([1 for i in range(1, 2*n, 2) if phi3_knowledge_summary_optimized_preds[i] == 1]) / n

accuracies['gpt4o_mini_knowledge_summary_optimized_TNR'] = sum([1 for i in range(0, 2*n, 2) if gpt4o_mini_knowledge_summary_optimized_preds[i] == 0]) / n
accuracies['gpt4o_mini_knowledge_summary_optimized_TPR'] = sum([1 for i in range(1, 2*n, 2) if gpt4o_mini_knowledge_summary_optimized_preds[i] == 1]) / n

accuracies['gpt4o_knowledge_summary_optimized_TNR'] = sum([1 for i in range(0, 2*n, 2) if gpt4o_knowledge_summary_optimized_preds[i] == 0]) / n
accuracies['gpt4o_knowledge_summary_optimized_TPR'] = sum([1 for i in range(1, 2*n, 2) if gpt4o_knowledge_summary_optimized_preds[i] == 1]) / n

print("Baseline (TNR):", accuracies['baseline_TNR'])
print("Baseline (TPR):", accuracies['baseline_TPR'])
print("Phi3 Knowledge Optimized (TNR):", accuracies['phi3_knowledge_summary_optimized_TNR'])
print("Phi3 Knowledge Optimized (TPR):", accuracies['phi3_knowledge_summary_optimized_TPR'])
print("GPT4o Mini Knowledge Optimized (TNR):", accuracies['gpt4o_mini_knowledge_summary_optimized_TNR'])
print("GPT4o Mini Knowledge Optimized (TPR):", accuracies['gpt4o_mini_knowledge_summary_optimized_TPR'])
print("GPT4o Knowledge Optimized (TNR):", accuracies['gpt4o_knowledge_summary_optimized_TNR'])
print("GPT4o Knowledge Optimized (TPR):", accuracies['gpt4o_knowledge_summary_optimized_TPR'])

# Calculate and print the F1 scores
baseline_f1 = f1_score(true_labels, baseline_preds)
phi3_knowledge_optimized_f1 = f1_score(true_labels, phi3_knowledge_summary_optimized_preds)
gpt4o_mini_knowledge_optimized_f1 = f1_score(true_labels, gpt4o_mini_knowledge_summary_optimized_preds)
gpt4o_knowledge_optimized_f1 = f1_score(true_labels, gpt4o_knowledge_summary_optimized_preds)

print("Baseline F1 Score:", baseline_f1)
print("Phi3 Knowledge Optimized F1 Score:", phi3_knowledge_optimized_f1)
print("GPT4o Mini Knowledge Optimized F1 Score:", gpt4o_mini_knowledge_optimized_f1)
print("GPT4o Knowledge Optimized F1 Score:", gpt4o_knowledge_optimized_f1)

# Create a DataFrame for the new results
results = pd.DataFrame({
    'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    'Number of Rows': [n],
    'Baseline F1 Score': [baseline_f1],
    'Phi3 Knowledge Optimized F1 Score': [phi3_knowledge_optimized_f1],
    'GPT4o Mini Knowledge Optimized F1 Score': [gpt4o_mini_knowledge_optimized_f1],
    'GPT4o Knowledge Optimized F1 Score': [gpt4o_knowledge_optimized_f1],
    'Baseline (TPR)': [accuracies['baseline_TPR']],
    'Baseline (TNR)': [accuracies['baseline_TNR']],
    'Phi3 Knowledge Optimized (TPR)': [accuracies['phi3_knowledge_summary_optimized_TPR']],
    'Phi3 Knowledge Optimized (TNR)': [accuracies['phi3_knowledge_summary_optimized_TNR']],
    'GPT4o Mini Knowledge Optimized (TPR)': [accuracies['gpt4o_mini_knowledge_summary_optimized_TPR']],
    'GPT4o Mini Knowledge Optimized (TNR)': [accuracies['gpt4o_mini_knowledge_summary_optimized_TNR']],
    'GPT4o Knowledge Optimized (TPR)': [accuracies['gpt4o_knowledge_summary_optimized_TPR']],
    'GPT4o Knowledge Optimized (TNR)': [accuracies['gpt4o_knowledge_summary_optimized_TNR']]
})

# Append the new results to the existing CSV file
results.to_csv("Knowledge_Filtering_results.csv", mode='a', header=not pd.io.common.file_exists("Knowledge_Filtering_results.csv"), index=False)