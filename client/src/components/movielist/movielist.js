import React from 'react';
import MovieItem from '../movieitem/movieitem';

import './movielist.css';

class MovieList extends React.Component {
    render() {
        const movies = this.props.movies.map(movie => {
            return <MovieItem movie={movie} key={movie.id} />;
        })
        return (
            <div className="movie-list">
                {movies}
            </div>
        );
    }
}

export default MovieList;