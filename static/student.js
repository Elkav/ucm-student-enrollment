function signOut() {
    localStorage.removeItem('authToken');
    
    // Redirect to the login page
    window.location.href = 'login.html';
    //fix this
}