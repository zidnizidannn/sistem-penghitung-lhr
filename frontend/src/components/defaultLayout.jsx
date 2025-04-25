import React from "react";
import { useState } from "react";
import { FaHome, FaChartLine, FaDatabase, FaHistory, FaTimes, FaBars } from "react-icons/fa";
import { BiSolidCctv } from "react-icons/bi";
import { useLocation } from "react-router-dom"

const DefaultLayout = ({ children }) => {
    const [isOpen, setIsOpen] = useState(true);
    const toggleSidebar = () => setIsOpen(!isOpen);

    const menuItems = [
        { name: "Dashboard", path: "/dashboard", icon: <FaHome size={30} /> },
        { name: "Real-time", path: "/real-time", icon: <BiSolidCctv size={30} /> },
        { name: "Data LHR", path: "/data-lhr", icon: <FaDatabase size={30} /> },
        { name: "Riwayat", path: "/history", icon: <FaHistory size={30} /> },
    ];

    const location = useLocation();

    const headTitle = () => {
        switch (location.pathname) {
            case "/dashboard":
                return "Dashboard";
            case "/real-time":
                return "Real-time Monitoring";
            case "/data-lhr":
                return "Data LHR";
            case "/history":
                return "Riwayat Deteksi";
            default:
                return "Halaman";
        }
    };

    return (
        <div className="h-screen flex">
            <aside className={`w-1/6 bg-gray-200 p-4 text-lg ${isOpen ? "w-fit" : "w-fit overflow-hidden"} transition ease-in-out duration-400 sticky`}>
                {isOpen ? (
                    <>
                        <h1 className="font-semibold mb-4 flex items-center">
                            <FaChartLine size={50} className="mr-4" />
                            Sistem Penghitungan LHR
                        </h1>
                        <ul className="space-y-4">
                            {menuItems.map((item) => (
                                <li key={item.path}>
                                    <a
                                        href={item.path}
                                        className="flex items-center px-4 py-2 hover:bg-blue-400 hover:text-white rounded-lg transition-all"
                                    >
                                        <span className="mr-3">
                                            {item.icon}
                                        </span>
                                        {item.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </>
                ) : (
                    <>
                        <h1 className="items-center mb-4">
                            <FaChartLine size={45} className="" />
                        </h1>
                        <ul className="space-y-4">
                            {menuItems.map((item) => (
                                <li key={item.path}>
                                    <a
                                        href={item.path}
                                        className="flex items-center px-4 py-2 hover:bg-blue-400 hover:text-white rounded-lg transition-all"
                                    >
                                        <span className="">{item.icon}</span>
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </>
                )}
            </aside>
            <div className="flex-1 overflow-auto">
                {/* Header */}
                <header className="p-6 bg-gray-200 h-fit w-full flex sticky top-0">
                    <button className="mr-2" onClick={toggleSidebar}>
                        <FaBars />
                    </button>
                    <h1 className="text-2xl font-semibold">{headTitle()}</h1>
                </header>

                {/* Konten Halaman */}
                <main className="p-6">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default DefaultLayout;
