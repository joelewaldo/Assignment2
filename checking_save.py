import shelve
import os


class SaveChecker:
    def __init__(self, frontier_save_file, max_save_file, token_save_file):
        self.frontier_save_file = frontier_save_file
        self.max_save_file = max_save_file
        self.token_save_file = token_save_file

        if not os.path.exists(self.frontier_save_file):
            # Save file does not exist, but request to load save.
            print("frontier_save_file does not exist")
            self.frontier_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.frontier_save = shelve.open(self.frontier_save_file)
        
        if not os.path.exists(self.max_save_file):
            # Save file does not exist, but request to load save.
            print("max_save_file does not exist")
            self.max_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.max_save = shelve.open(self.max_save_file)
        
        if not os.path.exists(self.token_save_file):
            # Save file does not exist, but request to load save.
            print("token_save_file does not exist")
            self.token_save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.token_save = shelve.open(self.token_save_file)

    def longest_page(self) -> tuple[str, str]:
        return (self.max_save['url'], self.max_save['max_words'])

    def common_words(self):
        # Sorting the dictionary by value and storing it as a list of tuples (key, value)
        mostFrequent = sorted(self.token_save.items(), key=lambda x: x[1], reverse=True)

        # If the dictionary has 50 or fewer items, return them all
        if len(mostFrequent) <= 50:
            return dict(mostFrequent)  # Convert list of tuples back to dictionary for consistency
        else:
            # Return the first 50 elements as a dictionary
            return dict(mostFrequent[:50])

    def generate_answer(self):
        with open("Answer.txt", "w") as file:
            file.write("Question 2: \n")
            longest_page = self.longest_page()
            file.write(f"     Longest page url is {longest_page[0]} with {longest_page[1]} words.\n")
            file.write("Question 3: \n")
            question_3 = self.common_words()
            for token, freq in question_3.items():
                file.write(f"     <{token}> -> <{freq}>\n")

            # file.write("Question 2: ")

    def __del__(self):
        self.frontier_save.close()
        self.max_save.close()
        self.token_save.close()


# '''
# Question 1:
# '''
# fl = "frontier.shelve"
# obj = SaveChecker(fl)
# print(obj.length())


# '''
# Question 2:
# '''
# f2 = "insert qusetion 2 save"
# obj = SaveChecker(f2)
# print(obj.length())

"""
Question 3:
"""
f3 = "token.shelve"
obj = SaveChecker(f3)
print(obj.generate_answer())


# '''
# Question 4:
# '''
# fl = "frontier.shelve"
# obj = SaveChecker(fl)
# print(obj.length())
