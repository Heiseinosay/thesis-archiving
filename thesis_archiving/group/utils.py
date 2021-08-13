from flask import flash, redirect
from werkzeug.exceptions import abort

def check_panelists(current_user, group):
    
    if current_user not in group.panelists:
            abort(403)

    if not group.chairman:
        flash("Please assign a chairman before proceeding.", "danger")
        return redirect('user.profile')

