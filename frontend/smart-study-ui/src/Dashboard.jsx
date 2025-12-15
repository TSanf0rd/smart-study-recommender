import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

export default function Dashboard() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem("user"))

  // Temporary mock data (replace with API later)
  const [courses, setCourses] = useState([
    {
      id: 1,
      title: "CS 4090 – Software Engineering",
      progress: 72,
    },
    {
      id: 2,
      title: "CS 5300 – Database Systems",
      progress: 45,
    },
    {
      id: 3,
      title: "IST 4410 – Information Systems",
      progress: 88,
    },
  ])

  useEffect(() => {
    if (!user) {
      navigate("/")
    }
  }, [user, navigate])

  if (!user) return null

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <section>
        <h1 className="text-2xl font-semibold">
          Welcome back, {`${user.username.charAt(0).toUpperCase()}${user.username.slice(1)}`}
        </h1>
        <p className="text-gray-600 mt-1">
          Role: {`${user.role.charAt(0).toUpperCase()}${user.role.slice(1)}`}
        </p>
      </section>

      {/* Courses Section */}
      <section>
        <h2 className="text-xl font-semibold mb-4">
          Your Courses
        </h2>

        {courses.length === 0 ? (
          <p className="text-gray-500">
            You are not enrolled in any courses yet.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-white rounded-lg shadow-sm border p-5"
              >
                <h3 className="font-medium mb-3">
                  {course.title}
                </h3>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-500 h-2 rounded-full"
                    style={{ width: `${course.progress}%` }}
                  />
                </div>

                <p className="text-sm text-gray-600 mt-2">
                  {course.progress}% complete
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
