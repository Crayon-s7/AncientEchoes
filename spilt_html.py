from bs4 import BeautifulSoup
import json

# Load the HTML content
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Extract content between <p class="border"> tags
def segment_between_borders(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div'])  # Adjust to capture relevant tags

    segmented_content = []
    current_segment = {"plain_text": "", "raw_html": ""}

    for element in elements:
        if element.name == 'p' and 'border' in element.get('class', []):
            if current_segment["plain_text"]:  # Save current segment if it's not empty
                segmented_content.append(current_segment)
                current_segment = {"plain_text": "", "raw_html": ""}
        else:
            text = element.get_text(strip=True)
            raw_html = str(element)
            current_segment["plain_text"] += text + "\n"
            current_segment["raw_html"] += raw_html + "\n"

    if current_segment["plain_text"]:  # Add last segment
        segmented_content.append(current_segment)

    return segmented_content

# Save the segmented content to a JSON file
def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # File paths
    input_path = '/Volumes/Data/EB/DEV/AncientEchoes/output.html'  # Replace with your HTML file path
    output_path = '/Volumes/Data/EB/DEV/AncientEchoes/output.json'  # Replace with your desired output file path

    # Process the HTML file
    html_content = load_html(input_path)
    segmented_content = segment_between_borders(html_content)

    # Create the final output structure
    output_data = {"segmented_content": segmented_content}

    # Save the result to a JSON file
    save_to_json(output_data, output_path)
    print(f"Segmented content saved to {output_path}")