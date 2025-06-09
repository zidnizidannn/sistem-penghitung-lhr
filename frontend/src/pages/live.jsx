import React, { useState } from "react";
import axios from "axios";
import DefaultLayout from "../components/defaultLayout";

const LiveDetection = () => {
    const [showStream, setShowStream] = useState(false);

    const handleStartDetection = async () => {
        try {
            const res = await axios.post("http://localhost:5000/api/start_detection");
            console.log(res.data.message);
            setShowStream(false); // reset dulu agar <img> reload
            setTimeout(() => setShowStream(true), 500); // delay sedikit agar backend siap
        } catch (err) {
            console.error(err.response?.data || err.message);
        }
    };

    const handleStopDetection = async () => {
        try {
            const res = await axios.post("http://localhost:5000/api/stop_detection");
            console.log(res.data.message);
            setShowStream(false);
        } catch (err) {
            console.error(err.response?.data || err.message);
        }
    };

    return (
        <DefaultLayout>
            <div className="flex flex-col items-center p-4">
                <h1 className="text-3xl font-bold text-center mt-8 mb-6">
                    Live Deteksi Kendaraan
                </h1>

                <div className="w-full max-w-4xl bg-white rounded-lg shadow-md p-4">
                    <div className="w-full overflow-hidden rounded-md">
                        {showStream && (
                            <img key={Date.now()} src="http://localhost:5000/api/video_feed" alt="Live Detection Stream" className="w-full h-auto rounded-md border"/>
                        )}
                    </div>
                </div>

                <div className="flex gap-4 mt-6">
                    <button
                        onClick={handleStartDetection}
                        className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-md transition duration-200"
                    >
                        Mulai Deteksi
                    </button>
                    <button
                        onClick={handleStopDetection}
                        className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-md transition duration-200"
                    >
                        Berhenti Deteksi
                    </button>
                </div>
            </div>
        </DefaultLayout>
    );
};

export default LiveDetection;
