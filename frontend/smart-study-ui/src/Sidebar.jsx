import { MoreVertical, ChevronLast, ChevronFirst, GraduationCap } from 'lucide-react'
import { useContext, createContext, useState } from 'react'


const SidebarContext = createContext({ expanded: true })

export default function Sidebar({ children }) {
  const [expanded, setExpanded] = useState(true)
  const user = JSON.parse(localStorage.getItem("user"))

  return (
    <aside
      className={`relative h-screen transition-all duration-300 ease-in-out ${
        expanded ? "w-64" : "w-14"
      } bg-gray-600 border-r z-20`}
    >
      {/* Logo + Toggle */}
      <div className={`flex items-center transition-all h-14 w-full`}>
        {/* App Icon */}
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/20">
        <GraduationCap className="text-indigo-400" size={22} />
        </div>

        {/* App Name */}
        <span
        className={`text-lg font-bold text-white tracking-tight
        transition-all duration-300 overflow-hidden ${
            expanded ? "w-40 opacity-100" : "w-0 opacity-0"
        }`}
        >
        SmartStudy
        </span>


        <nav className="h-full flex flex-col bg-white border-r shadow-sm" />

        <button
          onClick={() => setExpanded((curr) => !curr)}
          className="absolute top-4 -right-3 z-30
             flex items-center justify-center
             w-6 h-6 rounded-full
             bg-white shadow-md hover:bg-gray-100"
        >
          {expanded ? <ChevronFirst /> : <ChevronLast />}
        </button>
      </div>

      {/* Sidebar Items */}
      <SidebarContext.Provider value={{ expanded }}>
        <ul
          className={`rounded-lg transition-all ${
            expanded ? 'bg-[#333333] opacity-90' : 'flex flex-col items-center'
          }`}
        >
          {children}
        </ul>
      </SidebarContext.Provider>

      {/* User Section */}
      <div className="flex p-3 bg-[#333333] rounded-lg">
        <img
          src="https://ui-avatars.com/api/?background=c7d2fe&color=3730a3&bold=true"
          alt=""
          className="w-10 h-10 rounded-md"
        />

        <div
          className={`flex justify-between items-center overflow-hidden transition-all ${
            expanded ? 'w-52 ml-3' : 'w-0'
          }`}
        >
          <div className="leading-4">
            <h4 className="font-semibold">{user.name}</h4>
            <span className="text-s text-gray-200">
            {user.email}
            </span>
          </div>
          <MoreVertical size={20} />
        </div>
      </div>
    </aside>
  )
}

export function SidebarItem({ icon, text, active, alert, onClick }) {
  const { expanded } = useContext(SidebarContext)

  return (
    //Affects the color of hover and text on sidebar
    <li
      onClick={onClick}
      className={`relative flex items-center my-1 rounded-md cursor-pointer transition-colors group 
        ${expanded ? "w-full px-3 py-2" : "w-auto p-2 justify-center"}
        ${
            active
            ? 'bg-indigo-100 text-indigo-800'
            : expanded
            ? 'text-gray-100 hover:bg-indigo-400'
            : `text-gray-100 hover:bg-indigo-400`
        }`}
    >
      <div
        className={`flex items-center justify-center rounded-lg transition-all
            ${expanded ? "w-9 h-9" : "w-10 h-10"}
        `}
        >
        {icon &&
            icon.type &&
            icon.type.render && // safety for JSX elements
            icon.type.render({
            ...icon.props,
            size: expanded ? 20 : 24,
            })}
      </div>

      <span
        className={`overflow-hidden transition-all ${
          expanded ? 'w-52 ml-3' : 'w-0'
        }`}
      >
        {text}
      </span>

      {alert && (
        <div
          className={`absolute right-2 w-2 h-2 rounded bg-indigo-400 ${
            expanded ? '' : 'top-2'
          }`}
        />
      )}

      {!expanded && (
        <div
          className="absolute left-full rounded-md px-2 py-1 ml-2
          bg-indigo-100 text-indigo-800 text-sm
          invisible opacity-20 -translate-x-3 transition-all
          group-hover:visible group-hover:opacity-100 group-hover:translate-x-0"
        >
          {text}
        </div>
      )}
    </li>
  )
}
