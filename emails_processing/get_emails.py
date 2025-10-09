
def get_emails():
    while True:
        email=input("Enter you email or (type exit to quit): ")
        if email.lower() == "exit":
            break
        if "@" in email and "." in email:
            with open("email.txt", "a") as file:
                file.write(email + "\n")
            print("Email saved:", email)
        else:   
            print("Invalid email format. Please try again.")

if __name__ == "__main__":
    get_emails()
