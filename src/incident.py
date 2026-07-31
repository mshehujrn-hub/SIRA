class Incident:
    """
    Represents a single incident report.

    Every incident in our system will become an object of this class.
    """

    def __init__(self, incident_id, report_text):
        self.incident_id = incident_id
        self.report_text = report_text

    def display(self):
        print("-" * 50)
        print(f"Incident ID : {self.incident_id}")
        print(f"Report      : {self.report_text}")