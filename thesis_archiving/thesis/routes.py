from flask import Blueprint, render_template
from flask_login import login_required

thesis = Blueprint("thesis", __name__, url_prefix="/thesis")

# wrap whole blueprint to be login required
@thesis.before_request
@login_required

@thesis.route("/read")
def read():
    # login req

    thesis = [
        {
        "title":"Creation of LinEase Mobile Application: A Land Pollution Action Network in Manila",
        "program_name":"BSCS",
        "category_name":"PROPOSAL",
        "research_area":"Computer Applications / Social Computing",
        "research_keywords":['Land Pollution Tracker','Mapping Application','Camera API','Environmental Solution'],
        "overview":"LinEase is a land pollution action network created to monitor and spread awareness on land pollution while simultaneously serving as a platform to contribute in solving the issue on land pollution and the prevention of it. LinEase gathers data from individual people who have reported or issued polluted areas using images with descriptive captions. LinEase intends to serve those who understand the importance of the environment and keeping it as healthy as possible and hope to have a platform for them to spread awareness and/or even contribute by reporting any issue regarding land pollution in certain areas themselves.",
        },
        {
        "title":"Online Patient Information and Billing System for Nursing Homes",
        "program_name":"BSIT",
        "category_name":"COMPLETED",
        "research_area":"Patient Information and Billing System",
        "research_keywords":["Contagious Hope","Sci-Fi","Survival", "Thriller","Imagination Artistry",],
        "overview":"Once upon a time, there is a young boy named Tim. He is the grumpy and only son of his parents. One day her mother decided to go to the lighthouse but instead of telling the truth to Tim, she said that they will go to the beach for vacation. Tim has a traumatic incident in the lighthouse, that’s why whenever he remembers their lighthouse he always disregards the presence of it. In the middle of their trip, Tim wonders that the road is similar in the location of the lighthouse. Because of this, Tim is furious and he feels betrayed, knowing that he cannot go back to that place because that is where his father died. Because of that, he said to his mother to stop the car and he gets out of it to think. During his journey while walking suddenly there’s a rainfall, Tim cries reminiscing the memories with his father. ",
        }
    ]

    return render_template("thesis/read.html", thesis=thesis)
