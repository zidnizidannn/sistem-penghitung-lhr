import React from "react";

const Index = () => {
    return (
        <div className="min-h-screen w-full flex flex-col justify-center items-center">
            <h1 className="text-4xl font-bold text-center absolute top-20">SISTEM PENGHITUNGAN <br /> LALU LINTAS HARIAN RATA-RATA</h1>

            <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-md">
                <h1 className="text-xl font-semibold text-center mb-6">
                    Silahkan masuk sebagai Admin
                </h1>

                <form className="space-y-4 text-center">
                    <div className="space-y-4">
                        <input
                            type="text" placeholder="Masukkan username" className="w-full px-3 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />

                        <input
                            type="password" placeholder="Masukkan Password" className="w-full px-3 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <button
                        type="submit" className="w-fit bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md transition duration-200"
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

export default Index;
