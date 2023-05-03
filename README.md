# Team B-27 Transfer Guide Project

A website to assist students transferring into UVA transfer their credits: <https://transfer-guide.herokuapp.com/>

## Common Requirements
1) **Google Login**
    - If you're not already logged in, click on the "Continue with Google" button on the "Home" page.
    - To logout, navigate to the header dropdown and click "Log Out."

2) **User Access Levels**
    - New users are given "common" priveledges by default.
    - To gain "admin" priveledges, navigate to the header dropdown, click "Account Info," and enter the secure key (`admin` by default).

3) **SIS API**
    - Four semesters' worth of UVA courses are stored in our database.
    - To add older courses, navigate to the "Home" page, click "UVA SIS Lookup," and fill out the form.

## Transfer-Guide-Specific Requirements
1) **Search Course by Attributes**
    - Locate the "Course Search" on the "Home" page.
    - It will search UVA courses by default if no external college is provided.
    - To see a course's equivalencies, locate that course in the search results and view the "Course Equivalencies" list on its course page.

2) **Submit Request to Be Evaluated by Student's Advisor**
    - Click on a UVA course in the search results and locate the "Make Request" button on its course page.
    - Alternatively, see the [shopping cart](#additional-features) in the additional features.

3) **Admins Can Add/Edit Courses**
    - To add a course, navigate to the header and click "Add Course."
    - To edit an existing course, locate it in the search results and click "Edit Course" on its course page.

4) **Admins Can Accept/Reject Transfer Credit Requests**
    - Navigate to the header and click "View Requests." 
    - Under the "Recent Requests" list, click the ⋮ button beside a request to accept / reject / delete it. You can also switch between "pending," "accepted," "rejected," and "all" tabs.
    - Under the "Recent Users" list, you can view user-specific transfer requests.

5) **Students Can See the Status of Their Request**
    - Navigate to the header and click "View Requests." 
    - See colored progress bar; otherwise, cycle through "pending," "accepted," "rejected," and "all" tabs.
    - Click the ⋮ button beside a request to view the administrator's comment.
    - Alternatively, see the [notifications](#additional-features) in the additional features.

## Additional Features:
1) **Shopping Cart**
    - Stores one pre-existing internal course and one pre-existing external course.
    - Located on the "Home" page, but only visible after a course has been added.
    - To add a course, find that course in the search and visit its course page. Then, click "Add to Cart."
    - Tied to session (clears on logout, browser close, etc.)
    - Once full, the shopping cart can be used to submit a transfer request.

2) **Favorited Course Equivalencies**
    - To add a favorite, locate a course in the search, visit its course page, and view its "Course Equivalencies" list. From there, you can favorite / unfavorite accepted course equivalencies.
    - To view all of your favorites, navigate to the header dropdown and click "Favorites." Here, you can also see the cumulative credits.
    - "Favorited courses" (i.e., courses belonging to a favorited course equivalency) will be highlighted *green* in the search and in course equivalency lists.
    - Likewise, courses that are a single degree of separation away from a favorited course equivalency will be highlighted *yellow* in course equivalency lists.

3) **Notifications**
    - New notifications can be found on the bell icon in the header.
    - Notifications alert users to a change in status to one of their requests.
    - Click "View and Dismiss" to discard old notifications.

4) **Account Information**
    - To view one's own information, navigate to the header dropdown and click "Account Information." This page will display your username, first name, last name, email address, and account permissions.
    - For an administrator to view a user's information, navigate to the "View Requests" page and click on the ⋮ button beside a transfer request. Then, click the blue link displaying the user's name.

5) **Toggle Theme**
    - Navigate to the header dropdown and click "Toggle Theme."
    - Allows a user to toggle between a dark and light theme. The user's selection will be stored in the session.

6) **User's Last College**
    - A quality-of-life feature that stores a user's last searched college (from the "Course Search") or last added college (from the "Make Request" form) in the session.
    - The user's college will appear first in the dropdown college selector on certain forms.
    - The user's college will appear as its own tab under the "Course Equivalencies" list on UVA course pages.
