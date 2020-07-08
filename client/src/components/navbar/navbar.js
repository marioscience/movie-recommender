import React from 'react';

import './navbar.css';

class Navbar extends React.Component {
    render() {
        return (<div id="navbar">
                    <div className="header"><h1>Movie Recommender</h1></div>
                    <div className="links"><ul></ul></div>
                    <div className="user-box"></div>
                </div>);
    }
}

export default Navbar;