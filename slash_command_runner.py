#rfom supabase_integration import save_slides
import json

def run_slash_command(model, command, message_history,original_slides):
    print(f"Running slash command: {command}")
    if command.startswith("/save"):
        print("Saving slides...")
        print(f"Original Slides: {json.dumps(original_slides, indent=2)}")
        #print(f"Msg history: {json.dumps(message_history, indent=2)}")
    else:
        unknown_cmd_msg = f"Unknown command: {command}"
        print(unknown_cmd_msg)
        message_history.append({"role": "assistant", "content": unknown_cmd_msg})