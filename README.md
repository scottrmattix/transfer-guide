# Team B-27 Transfer Guide Project

A website to assist students transferring into UVA transfer their credits: <https://transfer-guide.herokuapp.com/>

# Requirements and Corresponding Features:
1) **Search course by attributes**
    * met by search on the Home page
3) **Submit request to be evaluated by student's advisor**
    * met via "make request button" on any page of any internal course, or via additional feature 1
5) **Admins can add/edit courses**
    * admins can add courses via add course page (button in header for admins)
7) **Admins can accept/reject transfer credit requests**
    * met by View Requests page (button in header for admins)
9) **Students can see the status of their request**
    * met by View Requests page (button in header for users)

# Additional Features:
1) **Shopping Cart**
    * Stores one interal course and one external course
    * Tied to session (clears on logout, browser close, etc)
    * Transfer request can be submitted from shopping cart once full

2) **Favorites**
    * Stores known course transfers
    * Allows user to save for later and view cummulative credits

3) **Notifications**
    * Notifies users upon a change to one of their requests
    * Acceptance or change of status notification
    
4) **Account Information**
    * Displays user's information such as username, email address, and account permissions
    
5) **Upgrade to Admin**
    * A means for a normal user to get an upgrade to an admin account through a secure key
    * By default the key is 'admin'
    
6) **Toggle Theme**
    * Allows users to toggle between a dark and light theme
