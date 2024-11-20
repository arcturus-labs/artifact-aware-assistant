import json
from flask import Blueprint, request, jsonify
from .conversation import Conversation, Artifact
from .tools import MarkdownArtifact, get_specify_questions_tool, set_up_tools
import requests
import uuid

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify(data.upper())


@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    user_message = messages[-1]['content']
    messages = messages[:-1]
    messages = unprocess_tool_uses_and_results(messages)
    artifacts = convert_to_artifacts(data.get('artifacts', []))
    
    markdown_artifact = artifacts[0] if artifacts else None
    assert markdown_artifact is not None, "No markdown artifact provided"
    assert isinstance(markdown_artifact, MarkdownArtifact), "Markdown artifact is not a MarkdownArtifact"
    tools = set_up_tools(markdown_artifact)
    try:
        conversation = Conversation(
            tools=tools,
            messages=messages,
            artifacts=artifacts,
        )
        response = conversation.say(user_message)
        messages = response['messages']
        artifacts = response['artifacts']
        
        return jsonify({
            'messages': process_tool_uses_and_results(messages),
            'artifacts': [artifact.dict() for artifact in artifacts],
            'status': 'success'
        })
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
    
def process_tool_uses_and_results(messages):
    processed_messages = []
    tool_uses_content = None
    
    for message in messages:
        if message['role'] == 'assistant' and isinstance(message['content'], list):
            # Store tool uses for next iteration
            tool_uses_content = message['content']
            continue
            
        if message['role'] == 'user' and isinstance(message['content'], list) and tool_uses_content:
            # Create mapping of tool_use_id to result content
            tool_results_map = {
                result['tool_use_id']: result['content']
                for result in message['content']
                if result['type'] == 'tool_result'
            }
            
            # Process the content list, replacing tool uses with combined use+result
            processed_content = []
            for item in tool_uses_content:
                if item.get('type') == 'tool_use':
                    processed_content.append({
                        'type': 'tool_use',
                        'name': item['name'],
                        'input': item['input'],
                        'output': tool_results_map[item['id']]
                    })
                else:
                    processed_content.append(item)
                    
            processed_messages.append({
                'role': 'assistant',
                'content': processed_content
            })
            tool_uses_content = None
            continue
            
        # Add any other messages as-is
        processed_messages.append(message)
        
    return processed_messages

def unprocess_tool_uses_and_results(messages):
    unprocessed_messages = []
    tool_use_counter = 0
    
    for message in messages:
        if message['role'] == 'assistant' and isinstance(message['content'], list):
            assistant_message_content = []
            user_message_content = []
            for item in message['content']:
                if item.get('type') == 'tool_use':
                    # Generate unique tool use ID
                    tool_use_id = f'toolu_{tool_use_counter}'
                    tool_use_counter += 1
                    
                    # Split tool use and result into separate messages
                    tool_use = {
                        'type': 'tool_use',
                        'id': tool_use_id,
                        'name': item['name'],
                        'input': item['input']
                    }
                    assistant_message_content.append(tool_use)
                    
                    # Store tool result for later
                    user_message_content.append({
                        'type': 'tool_result',
                        'tool_use_id': tool_use_id,
                        'content': item['output'],
                    })
                else:
                    assistant_message_content.append(item)
            
            unprocessed_messages.append({
                'role': 'assistant',
                'content': assistant_message_content
            })
            unprocessed_messages.append({
                'role': 'user',
                'content': user_message_content
            })
        else:
            # Add any other messages as-is
            unprocessed_messages.append(message)
    
    return unprocessed_messages


def convert_to_artifacts(artifacts):
    artifact_list = []
    for artifact in artifacts:
        if 'root' in artifact:
            artifact_list.append(MarkdownArtifact(identifier=artifact['identifier'], title=artifact['title'], markdown=artifact))
        else:
            artifact_list.append(Artifact(**artifact))
    return artifact_list

@api_bp.route('/choose_llm_txt', methods=['POST'])
def choose_llm_txt():
    try:
        data = request.get_json()
        url = data.get('url')
        name = data.get('name')
        
        if not url:
            return jsonify({
                'error': 'No URL provided',
                'status': 'error'
            }), 400
        
        # Fetch the LLM.txt content
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        markdown = response.text
        
        # Create an artifact with the content
        artifact = MarkdownArtifact(identifier='llm_text', title=f"{name.title()} LLM.txt", markdown=markdown)

        specify_questions_tool = get_specify_questions_tool()
        conversation = Conversation(
            tools=[specify_questions_tool],
            artifacts=[artifact],
            model="claude-3-5-haiku-20241022",
        )
        # don't care about the response, just getting the questions from the tool call
        _ = conversation.say("Specify 5 interesting examples quesetions about the attached artifact.")
        
        questions = specify_questions_tool.callable.questions

        return jsonify({
            'artifact': artifact.dict(),
            'questions': questions,
        })
        
    except requests.RequestException as e:
        print(f"Error in chat endpoint: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Failed to fetch LLM.txt: {str(e)}',
            'status': 'error'
        }), 500
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

