"use client";

import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { SimilarMovies } from "@/types/analysis";

interface SimilarMoviesCarouselProps {
  similarMovies?: SimilarMovies[]; // optional array
}

export default function SimilarMoviesCarousel({ similarMovies = [] }: SimilarMoviesCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToIndex = (index: number) => {
    if (containerRef.current) {
      const container = containerRef.current;
      const child = container.children[index] as HTMLElement;
      if (child) {
        container.scrollTo({ left: child.offsetLeft, behavior: "smooth" });
      }
    }
  };

  const handlePrev = () => {
    const newIndex = Math.max(currentIndex - 1, 0);
    setCurrentIndex(newIndex);
    scrollToIndex(newIndex);
  };

  const handleNext = () => {
    const newIndex = Math.min(currentIndex + 1, similarMovies.length - 1);
    setCurrentIndex(newIndex);
    scrollToIndex(newIndex);
  };

  useEffect(() => {
    scrollToIndex(currentIndex);
  }, [currentIndex, similarMovies]);

  return (
    <div className="max-w-4xl mx-auto bg-gray-900/80 border border-gray-800 rounded-xl p-6 shadow-xl hover:shadow-indigo-900/20 transition flex flex-col">
      <h2 className="text-2xl font-semibold text-indigo-400 mb-4">Similar Movies</h2>

      <div className="relative flex items-center">
        {/* Prev button */}
        <button
          onClick={handlePrev}
          disabled={currentIndex === 0}
          className="p-2 rounded-full bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed text-white mr-2 transition"
          aria-label="Previous"
        >
          &#8592;
        </button>

        {/* Scroll container */}
        <div
          ref={containerRef}
          className="overflow-x-auto scroll-smooth scrollbar-hide flex snap-x snap-mandatory space-x-4"
        >
          {similarMovies.map((movie, index) => (
            <div
              key={`${movie.Title}-${movie.Year}`} // unique key
              className="shrink-0 w-40 snap-start bg-gray-800 rounded-lg overflow-hidden shadow cursor-pointer hover:shadow-indigo-600 transition"
            >
              <Image
                src={movie.Poster}
                alt={`${movie.Title} Poster`}
                width={160}
                height={240}
                className="object-cover w-full h-60"
                loading="lazy"
                unoptimized={false} // set true if domain not configured
              />
              <div className="p-2 text-center">
                <h3 className="text-indigo-300 font-semibold text-sm truncate">{movie.Title}</h3>
                <p className="text-gray-400 text-xs mt-1">{movie.Year}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Next button */}
        <button
          onClick={handleNext}
          disabled={currentIndex === similarMovies.length - 1}
          className="p-2 rounded-full bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed text-white ml-2 transition"
          aria-label="Next"
        >
          &#8594;
        </button>
      </div>
    </div>
  );
}
