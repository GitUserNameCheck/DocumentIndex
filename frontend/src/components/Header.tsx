import { useState } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import {
  Home,
  Menu,
  Table2,
  X,
} from 'lucide-react'
import { setStoredUser, useAuth } from '@/integrations/auth/root-provider';
import { tryCatch } from '@/utils/try-catch';


export default function Header() {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const auth = useAuth()


    const onClick = async () => {
  
      const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + "/auth/logout", {
        method: "POST",
        credentials: "include"
      }));
  
      if (error) {
        alert(error.message);
        return;
      }
  
      const data = await res.json();
  
      if (!res.ok) {
        alert(data["detail"])
        return;
      }
  
      setStoredUser(null, auth)
  
      navigate({
        to: '/',
      })
    }


  return (
    <>
      <header className="p-4 flex items-center bg-gray-800 shadow-lg text-xl font-semibold">
        <button
          onClick={() => setIsOpen(true)}
          className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Open menu"
        >
          <Menu size={24} />
        </button>
        <div className="flex flex-row w-full justify-between items-center">
          <h1 className="ml-4">
            <Link to="/">
              Document Index
            </Link>
          </h1>
          <div className="flex flex-row gap-5 items-center">
            {auth.user && <h1>
              {auth.user}
            </h1>}
            {auth.user && <h1 className="border-1 rounded p-1">
              <button className="cursor-pointer" onClick={() => onClick()}>
                Logout
              </button>
            </h1>}
            {!auth.user && <h1>
              <Link to="/login">
                Sign in
              </Link>
            </h1>}
            {!auth.user && <h1 className="border-1 rounded p-1">
              <Link to="/register">
                Sign up
              </Link>
            </h1>}
          </div>
        </div>
      </header>

      <aside
        className={`fixed top-0 left-0 h-full w-80 bg-gray-900 border-r-1 border-gray-700 z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">Navigation</h1>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            aria-label="Close menu"
          >
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto">
          <Link
            to="/"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-800 transition-colors mb-2"
          // activeProps={{
          //     className:
          //         'flex items-center gap-3 p-3 rounded-lg bg-cyan-600 hover:bg-cyan-700 transition-colors mb-2',
          // }}
          >
            <Home size={20} />
            <span className="font-medium">Home</span>
          </Link>

          {auth.user && <Link
            to="/documents"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-800 transition-colors mb-2"
          // activeProps={{
          //     className:
          //         'flex items-center gap-3 p-3 rounded-lg bg-cyan-600 hover:bg-cyan-700 transition-colors mb-2',
          // }}
          >
            <Table2 size={20} />
            <span className="font-medium">Documents</span>
          </Link>}

        </nav>
      </aside>
    </>
  )
}