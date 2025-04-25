import React from "react";

const DownloadButton = () =>{
    return(
        <div className="relative inline-block text-left">
            <div>
                <button
                    type="button"
                    className="inline-flex justify-center w-full rounded-md bg-blue-600 text-white px-4 py-2 text-sm font-medium hover:bg-blue-700 focus:outline-none"
                    id="menu-button"
                    aria-expanded="true"
                    aria-haspopup="true"
                >
                    Download
                </button>
            </div>

            <div
                className="origin-top-left absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="menu-button"
            >
                <div className="py-1" role="none">
                    <button
                        onClick={() => handleDownload("daily", "csv")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Harian (CSV)
                    </button>
                    <button
                        onClick={() => handleDownload("weekly", "csv")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Mingguan (CSV)
                    </button>
                    <button
                        onClick={() => handleDownload("monthly", "csv")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Bulanan (CSV)
                    </button>
                    <hr className="my-1" />
                    <button
                        onClick={() => handleDownload("daily", "pdf")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Harian (PDF)
                    </button>
                    <button
                        onClick={() => handleDownload("weekly", "pdf")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Mingguan (PDF)
                    </button>
                    <button
                        onClick={() => handleDownload("monthly", "pdf")}
                        className="text-gray-700 block px-4 py-2 text-sm w-full text-left hover:bg-gray-100"
                    >
                        Bulanan (PDF)
                    </button>
                </div>
            </div>
        </div>
    )
}

export default DownloadButton