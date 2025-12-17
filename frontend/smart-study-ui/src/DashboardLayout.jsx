import Sidebar, { SidebarItem } from "./Sidebar"
import { Outlet, useNavigate } from "react-router-dom"
import {
  LayoutDashboard,
  Video,
  UserCircle,
  Settings,
  LogOut,
  LibraryBig
} from "lucide-react"

export default function DashboardLayout() {
  const navigate = useNavigate()

  return (
    <div className="flex h-screen w-screen">
      <Sidebar>
        <SidebarItem
          icon={<LayoutDashboard size={20} />}
          text="Dashboard"
          onClick={() => navigate("/dashboard")}
        />

        <SidebarItem
          icon={<LibraryBig />}
          text="Resources"
          onClick={() => navigate("/resources")}
        />

        <SidebarItem
          icon={<Video size={20} />}
          text="Videos"
          onClick={() => navigate("/videos")}
        />

        <SidebarItem
          icon={<UserCircle size={20} />}
          text="Profile"
          onClick={() => navigate("/profile")}
        />

        <SidebarItem
          icon={<Settings size={20} />}
          text="Settings"
          onClick={() => navigate("/settings")}
        />

        <SidebarItem
          icon={<LogOut size={20} />}
          text="Logout"
          alert
          onClick={() => {
            localStorage.removeItem("user")
            navigate("/")
          }}
        />


      </Sidebar>

      {/* Page content swaps here */}
      <main className="flex-1 overflow-auto bg-[#F7F9FC] p-6">
        <Outlet />
      </main>
    </div>
  )
}
