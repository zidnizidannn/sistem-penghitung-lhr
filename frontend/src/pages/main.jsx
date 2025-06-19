import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Main = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        
        if (!username || !password) {
            setError("Username dan password harus diisi");
            return;
        }

        try {
            const response = await axios.post("http://localhost:5000/api/login", {
                username,
                password
            });
            
            localStorage.setItem("token", response.data.token);
            
            navigate("/dashboard");
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error || "Login gagal");
            } else if (err.request) {
                setError("Tidak ada respon dari server");
            } else {
                setError("Terjadi kesalahan saat mengirim permintaan");
            }
        }
    };

    return (
        <div className="min-h-screen w-full flex flex-col justify-center items-center">
            <h1 className="text-4xl font-bold text-center absolute top-20">SISTEM PENGHITUNGAN <br /> LALU LINTAS HARIAN RATA-RATA</h1>

            <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-md">
                <h1 className="text-xl font-semibold text-center mb-6">
                    Silahkan masuk sebagai Admin
                </h1>

                {error && (
                    <div className="mb-4 p-2 bg-red-100 text-red-700 text-sm rounded">
                        {error}
                    </div>
                )}

                <form className="space-y-4 text-center" onSubmit={handleLogin}>
                    <div className="space-y-4">
                        <input
                            type="text" 
                            placeholder="Masukkan username" 
                            className="w-full px-3 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />

                        <input
                            type="password" 
                            placeholder="Masukkan Password" 
                            className="w-full px-3 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit" className="w-fit bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md transition duration-200 cursor-pointer"
                    >
                        Masuk
                    </button>
                </form>

                <p className="text-xs text-gray-500 mt-4 text-center">
                    * Jika berkebutuhan khusus hubungi pihak terkait untuk akses masuk sistem
                </p>
            </div>
        </div>
    );
};

export default Main;