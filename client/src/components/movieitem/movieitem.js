import React from 'react';

import './movieitem.css';
import {Link} from "react-router-dom";

function MovieItem(props) {
    const runtimeHr = Math.floor(props.movie.runtime);
    const runtimeMn = (props.movie.runtime - runtimeHr) * 60;
    let imdb_rating_section = '';
    if (props.movie.imdb_rating) {
        imdb_rating_section = <span>{props.movie.imdb_rating.toFixed(2)}</span>;
    }

    return (
        <Link to={{pathname:`/movie/${props.movie.id}`, state: 'flush'}} >
            <div className="movie-item">
                <img src={props.movie.poster_url} alt=""/>
                <h3>{props.movie.title}</h3>
                <div className="detail-section">
                    <span>{props.movie.tagline}</span><br/>
                    <span><strong>Release Date: </strong>{new Date(props.movie.release_date).toLocaleDateString()}</span><br/>
                    <span><strong>Runtime: </strong>{runtimeHr + ":" + ("0" + runtimeMn).slice(-2)}</span><br/>
                    {imdb_rating_section}
                </div>
            </div>
        </Link>
    );
}

export default MovieItem;