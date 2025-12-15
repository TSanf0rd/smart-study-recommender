import { useState } from "react"
import ReactPlayer from "react-player"

const VIDEOS = [
  {
    id: 1,
    title: "React Basics Tutorial",
    url: "https://www.youtube.com/watch?v=SqcY0GlETPk",
  },
  {
    id: 2,
    title: "JavaScript Crash Course",
    url: "https://www.youtube.com/watch?v=hdI2bqOjy3c",
  },
  {
    id: 3,
    title: "Tailwind CSS in 20 Minutes",
    url: "https://www.youtube.com/watch?v=pfaSUYaSgRo",
  },
]

export default function Videos() {
  const [activeVideo, setActiveVideo] = useState(null)

  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Videos</h1>

      {/* Video Player */}
      {activeVideo && (
        <div className="mb-8 aspect-video max-w-4xl">
          <ReactPlayer
            url={activeVideo.url}
            controls
            width="100%"
            height="100%"
          />
          <h2 className="mt-2 text-lg font-medium">
            {activeVideo.title}
          </h2>
        </div>
      )}

      {/* Video Previews */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {VIDEOS.map((video) => (
          <div
            key={video.id}
            onClick={() => setActiveVideo(video)}
            className="cursor-pointer rounded-lg overflow-hidden bg-gray-900 hover:ring-2 hover:ring-indigo-400 transition"
          >
            {/* Thumbnail */}
            <img
              src={`https://img.youtube.com/vi/${getVideoId(video.url)}/hqdefault.jpg`}
              alt={video.title}
              className="w-full aspect-video object-cover"
            />

            {/* Title */}
            <div className="p-3 text-white text-sm">
              {video.title}
            </div>
          </div>
        ))}
      </div>
    </main>
  )
}

/* Helper to extract YouTube ID */
function getVideoId(url) {
  return url.split("v=")[1]
}
