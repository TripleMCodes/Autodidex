*from flask import render\_template, request, redirect, url\_for, flash, Blueprint, g*

*import logging*

*logging.basicConfig(level=logging.DEBUG)*

*from models import Message, User, Admin*

*from app import db*



*contct = Blueprint(*

&nbsp;   \*"contact",\*

    \*\\\_\\\_name\\\_\\\_,\*

    \*template\\\_folder="html css js",\*

    \*static\\\_folder="html css js",\*

    \*static\\\_url\\\_path="/contact/static"\*


*)*



*@contct.route('/contact', methods=\['GET', 'POST'])*

*def contact\_route():*

&nbsp;   \*if request.method == 'POST':\*

        \*name = request.form.get('name')\*

        \*email = request.form.get('email')\*

        \*# project\\\_type = request.form.get('projectType')\*

        \*# budget = request.form.get('budget')\*

        \*message = request.form.get('message')\*

        \*nda\\\_requested = 'nda' in request.form\*



        \*if not all(\\\[name, email, message]):\*

            \*if request.headers.get('X-Requested-With') == 'XMLHttpRequest':\*

                \*return {'success': False, 'message': 'All fields are required'}, 400\*

            \*flash('All fields are required', 'error')\*

            \*return redirect(url\\\_for('contact.contact\\\_route'))\*



        \*new\\\_message = Message(\*

            \*artist\\\_id=g.artist\\\_id,\*

            \*name=name,\*

            \*email=email,\*

            \*message=message,\*

            \*nda\\\_requested=nda\\\_requested\*

        \*)\*

        \*db.session.add(new\\\_message)\*

        \*db.session.commit()\*



        \*if request.headers.get('X-Requested-With') == 'XMLHttpRequest':\*

            \*return {'success': True, 'message': 'Message sent successfully! I\\\\'ll respond within 48 hours.'}, 200\*



        \*flash('Message sent successfully! I\\\\'ll respond within 48 hours.', 'success')\*

        \*return redirect(url\\\_for('contact.contact\\\_route'))\*

    

    \*admin = Admin.query.filter\\\_by(artist\\\_id=g.artist\\\_id).first()\*

    \*email = admin.email if admin else None\*

    \*user = User.query.filter\\\_by(artist\\\_id=g.artist\\\_id).first()\*

    \*name = user.name.upper() if user else ''\*

    \*return render\\\_template('contact.html', name=name, email=email)\*


