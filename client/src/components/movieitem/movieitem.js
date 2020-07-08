import React from 'react';

import './movieitem.css';
import {Link} from "react-router-dom";

function MovieItem(props) {
    return (
        <Link to={`/movie/${props.movie.id}`}>
            <div className="movie-item">
                <img src={props.movie.poster} alt=""/>
                <h3>{props.movie.title}</h3>
                <div className="detail-section">
                    <span>{props.movie.tagline}</span><br/>
                    <span>{props.movie.release_date}</span><br/>
                    <span>{props.movie.runtime}</span><br/>
                    <span>{props.movie.imdb_rating}</span>
                </div>
            </div>
        </Link>
    );
}

export default MovieItem;