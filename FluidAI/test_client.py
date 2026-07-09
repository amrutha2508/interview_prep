import requests
import json
import os

URL = "http://127.0.0.1:8000/agent"

def run_interactive_session():
    print("=" * 60)
    print("🤖 Welcome to the Autonomous Document Agent Terminal Client 🤖")
    print("=" * 60)
    
    # 1. Initialize the document request
    user_prompt = input("\nEnter your document request (e.g., 'Write a technical design for a payment system'):\n> ")
    if not user_prompt.strip():
        print("Request cannot be empty. Exiting.")
        return

    payload = {"request": user_prompt}
    
    print("\n[Thinking] Initializing agent thread and creating plan...")
    response = requests.post(URL, json=payload)
    
    if response.status_code != 200:
        print(f"Error initializing agent: {response.text}")
        return

    data = response.json()
    thread_id = data["thread_id"]

    # --- NEW: DISPLAY THE WHOLE PLAN AT THE TOP ---
    if "execution_plan" in data and data["execution_plan"]:
        print("\n" + "*" * 15)
        print("📋 AGENT'S GENERATED EXECUTION PLAN:")
        print("*" * 15)
        for step_num, section in enumerate(data["execution_plan"], start=1):
            print(f"  [ ] Step : {section}")
        print("*" * 15 + "\n")
    
    # 2. Enter the Human-in-the-Loop Review Cycle
    while data["status"] == "paused_for_review":
        review = data["review_payload"]
        current_step = data["current_step"]
        total_steps = data["total_steps"]
        
        print("\n" + "=" * 50)
        print(f"📋 SECTION FOR REVIEW [{current_step}/{total_steps}]: {review['section_title']}")
        print("=" * 50)
        print(review["drafted_content"])
        print("=" * 50)
        
        # Get feedback from terminal operator
        print("\n🤔 What would you like to do?")
        print("👉 Press [ENTER] to APPROVE and proceed to the next section.")
        print("👉 Or type your REVISION FEEDBACK below to make the agent rewrite it:")
        feedback = input("> ")
        
        # Post the feedback or approval back to the exact same thread
        payload = {
            "thread_id": thread_id,
            "feedback": feedback
        }
        
        print("\n[Processing] Sending input to agent state ...")
        response = requests.post(URL, json=payload)
        
        if response.status_code != 200:
            print(f"Error during state transition: {response.text}")
            return
            
        data = response.json()

    # 3. Handle Completion Workflow
    if data["status"] == "completed":
        print("\n" + "🎉" * 20)
        print("SUCCESS: Document generation complete!")
        print("🎉" * 20)
        print("logs:")
        for log in data.get("logs", []):
            print(f"  - {log}")

if __name__ == "__main__":
    run_interactive_session()