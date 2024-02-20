from chatbot_prototype import StudyChatBot


if __name__ == '__main__':

    # init chatbot
    chatbot = StudyChatBot()

    # Main loop for terminal interaction
    print("Welcome to Study ChatBot. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        
        # Check if the user wants to quit
        if user_input.lower() == 'quit':
            print("Exiting Study ChatBot. Goodbye!")
            break
        
        # Get response from the chatbot and display it
        response = chatbot.query(user_input)
        print("Study ChatBot:", response)