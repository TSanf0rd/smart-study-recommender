import { useEffect, useState } from "react";
import {
  getResourceDetails,
  logResourceView,
  rateResource,
  uploadResource,
  getResourcesByUploader
} from "./api/resources.api";

export default function Resources() {
  // ───────── State ─────────
  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState(0);
  const [myResources, setMyResources] = useState([]);
  const [selectedResourceId, setSelectedResourceId] = useState(null);

  // Tutor upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [difficultyLevel, setDifficulty] = useState("beginner");
  const [resourceType] = useState("study-guide");
  const [uploading, setUploading] = useState(false);


  // Auth info
  const user = JSON.parse(localStorage.getItem("user"));
  const userId = user?.user_id;
  const role = user?.role;
  const isTutor = role === "tutor";

  // ───────── Load tutor resources ─────────
  useEffect(() => {
    if (!isTutor || !userId) return;

    getResourcesByUploader(userId)
      .then((data) => {
        setMyResources(data);
      })
      .catch((err) => {
        console.error("Failed to load tutor resources", err);
      });
  }, [isTutor, userId]);

  // ───────── Load selected resource (QUERY) ─────────
  useEffect(() => {
    if (!selectedResourceId) {
      setResource(null);
      setLoading(false);
      return;
    }

    const loadResource = async () => {
      try {
        setLoading(true);
        const data = await getResourceDetails(selectedResourceId);
        setResource(data);
      } catch (err) {
        if (err.response?.status === 404) {
          // Expected empty state
          setResource(null);
        } else {
          console.error("Failed to load resource", err);
        }
      } finally {
        setLoading(false);
      }
    };

    loadResource();
  }, [selectedResourceId]);

  // ───────── Log view (COMMAND) ─────────
  const handleView = async () => {
    if (!selectedResourceId) return;

    try {
      await logResourceView(selectedResourceId, {
        user_id: userId,
        view_duration_seconds: 120,
        device_type: "desktop",
        session_id: crypto.randomUUID(),
      });
    } catch (err) {
      console.error("Failed to log view", err);
    }
  };

  // ───────── Rate resource (COMMAND) ─────────
  const handleRate = async () => {
    if (!rating || !selectedResourceId) return;

    try {
      const data = await rateResource(selectedResourceId, {
        user_id: userId,
        rating_value: rating,
        review_text: "",
      });

      setResource((prev) =>
        prev
          ? {
              ...prev,
              average_rating: data.updated_stats.average_rating,
            }
          : prev
      );
    } catch (err) {
      console.error("Failed to rate resource", err);
    }
  };

  // ───────── Upload resource (Tutor) ─────────
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file before uploading");
      return;
    }
  
    try {
      setUploading(true); 
  
      const formData = new FormData();
      formData.append("title", title);
      formData.append("description", description);
      formData.append("resource_type", resourceType);
      formData.append("difficulty_level", difficultyLevel);
      formData.append("uploader_user_id", userId);
      formData.append("file", selectedFile);
  
      const result = await uploadResource(formData);

      // RE-QUERY READ MODEL
      const refreshed = await getResourcesByUploader(userId);
      setMyResources(refreshed.data);

      setSelectedResourceId(result.data.resource_id);
      setShowUploadForm(false);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };
  

  // ───────── Render ─────────
  return (
    <div className="p-6 max-w-2xl relative">
      {/* Loading */}
      {loading && <p className="p-6">Loading resource...</p>}

      {/* Empty State */}
      {!loading && !selectedResourceId && !resource && (
        <div className="flex flex-col items-start gap-4">
          <p className="text-gray-600 text-lg">No resource selected yet.</p>

          {isTutor && (
            <>
              <p className="text-sm text-gray-500">
                Upload a resource to get started.
              </p>
              <button
                onClick={() => setShowUploadForm(true)}
                className="mt-2 px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
              >
                Upload Resource
              </button>
            </>
          )}
        </div>
      )}

      {/* Resource View */}
      {!loading && selectedResourceId && resource && (
        <>
          <h1 className="text-2xl font-bold">{resource.title}</h1>

          <p className="mt-2 text-gray-600">Views: {resource.view_count}</p>
          <p className="text-gray-600">
            Average Rating: {resource.average_rating}
          </p>

          <button
            onClick={handleView}
            className="mt-4 px-4 py-2 bg-indigo-500 text-white rounded"
          >
            View Resource
          </button>

          <div className="mt-6">
            <label className="mr-2 font-medium">Rate this resource:</label>
            <select
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
              className="border px-2 py-1 rounded"
            >
              <option value={0}>Select</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>

            <button
              onClick={handleRate}
              className="ml-3 px-3 py-1 bg-green-500 text-white rounded"
            >
              Submit Rating
            </button>
          </div>
        </>
      )}

      {/* Upload Modal */}
      {isTutor && showUploadForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
            <h2 className="text-xl font-semibold mb-4">
              Upload New Resource
            </h2>

            <input
              className="block w-full mb-2 border p-2 rounded"
              placeholder="Title"
              onChange={(e) => setTitle(e.target.value)}
            />

            <textarea
              className="block w-full mb-2 border p-2 rounded"
              placeholder="Description"
              onChange={(e) => setDescription(e.target.value)}
            />

            <select
              className="block w-full mb-2 border p-2 rounded"
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>

            <input
              type="file"
              className="block w-full mb-4"
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowUploadForm(false)}
                className="px-4 py-2 rounded border"
              >
                Cancel
              </button>

              <button
                onClick={handleUpload}
                className="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}

      {uploading && (
        <div className="mt-4 h-3 w-full bg-indigo-200 rounded-full animate-pulse" />
      )}

      {/* Tutor Resource List */}
      {isTutor && myResources.length > 0 && (
        <section className="mt-6">
          <h3 className="font-semibold">My Resources</h3>
          <ul className="mt-2 space-y-1">
            {myResources
            .filter(r => r.title && r.title.trim() !== "")
            .map((r) => (
              <li
                key={r.resource_id}
                className={`cursor-pointer p-2 rounded ${
                  selectedResourceId === r.resource_id
                    ? "bg-indigo-100"
                    : "hover:bg-gray-100"
                }`}
                onClick={() => setSelectedResourceId(r.resource_id)}
              >
                {r.title}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
