from data_processor import JiraDataProcessor

# Initialize processor
processor = JiraDataProcessor(
    input_dir="jira_data",        # Where your raw extracted Jira data is
    output_dir="processed_data"   # Where processed files will be saved
)

# Replace with actual file names in your jira_data directory
issues_file = "jira_complete_data_PROJECT_20250421_123456.json"
comments_file = "jira_comments_PROJECT_20250421_123456.json"
sprints_file = "jira_sprints_PROJECT_20250421_123456.json"
epics_file = "jira_epics_PROJECT_20250421_123456.json"

# Process data
df_issues = processor.process_issues(issues_file)
df_comments = processor.process_comments(comments_file)
df_sprints = processor.process_sprints(sprints_file)
df_epics = processor.process_epics(epics_file)

# Merge it
merged_df = processor.merge_data(df_issues, df_comments, df_sprints, df_epics)

# Create vector-ready file
vector_data = processor.create_vector_ready_data(merged_df)

# Save to JSON
import json
with open("processed_data/vector_ready_data.json", "w", encoding="utf-8") as f:
    json.dump(vector_data, f, indent=2, ensure_ascii=False)

print("✅ vector_ready_data.json created successfully.")
