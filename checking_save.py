import shelve
import os


class SaveChecker:
    def __init__(self, filename):
        self.filename = filename

        if not os.path.exists(self.filename):
            # Save file does not exist, but request to load save.
            print("Save file does not exist")
            self.save = None

        else:  # Load existing save file, or create one if it does not exist.
            self.save = shelve.open(self.filename)

    def length(self):
        return len(self.save)

    def longest_page(self):
        return """self.save['attribute for max']"""

    def common_words(self):
        # Sorting the dictionary by value and storing it as a list of tuples (key, value)
        mostFrequent = sorted(self.save.items(), key=lambda x: x[1], reverse=True)

        # If the dictionary has 50 or fewer items, return them all
        if len(mostFrequent) <= 50:
            return dict(mostFrequent)  # Convert list of tuples back to dictionary for consistency
        else:
            # Return the first 50 elements as a dictionary
            return dict(mostFrequent[:50])

    def generate_answer(self):
        with open("Answer.txt", "w") as file:
            file.write("Question 3: \n")
            question_3 = self.common_words()
            for token, freq in question_3.items():
                file.write(f"     <{token}> -> <{freq}>\n")

            # file.write("Question 2: ")

    def __del__(self):
        self.save.close()


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
