class ImprovementTrendEvaluator:
    def __init__(self):
        self.previous_feedback = None
        self.current_feedback = None
        self.no_improvement_flag = False

    def update_feedback(self, new_feedback):
        """Update the evaluator with new feedback from the validator."""
        # Shift current feedback to previous and update current with new feedback
        self.previous_feedback = self.current_feedback
        self.current_feedback = new_feedback
        self.evaluate_improvement()

    def evaluate_improvement(self):
        """Check if there is any improvement in the feedback."""
        if self.previous_feedback is not None and self.current_feedback is not None:
            # Set flag to True if there is no improvement (same errors)
            if self.previous_feedback == self.current_feedback:
                self.no_improvement_flag = True
            else:
                self.no_improvement_flag = False

    def get_no_improvement_flag(self):
        """Return the no improvement flag status."""
        return self.no_improvement_flag

    def print_status(self):
        """Print the current status of improvement."""
        if self.no_improvement_flag:
            print("No improvement between the last two feedbacks.")
        else:
            print("Improvement detected or insufficient data for comparison.")