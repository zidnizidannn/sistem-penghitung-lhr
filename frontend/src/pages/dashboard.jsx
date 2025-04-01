import React, { useState, useEffect } from "react";
import DefaultLayout from "../components/defaultLayout";
import axios from "axios";

const Dashboard = () => {
    const [data, setData] = useState({
        totalHariIni: 0,
        rataRataHarian: 0,
        perubahanDariKemarin: 0,
        jamSibuk: "00.00 - 00.00",
        jumlahKendaraanSibuk: 0
    });
    
    useEffect(() => {
        // Total Kendaraan Hari Ini
        axios.get("http://localhost:5000/api/vehicle_count/today")
        .then((response) => {
            console.log("API Response Today:", response.data);
            const total = response.data.reduce((sum, item) => sum + item.count, 0);
            setData((prev) => ({ ...prev, totalHariIni: total }));
        }).catch((error) => console.error("Error fetching vehicle count today:", error));
    
        // Rata-rata Harian
        axios.get("http://localhost:5000/api/vehicle_count/last_24h")
        .then((response) => {
            console.log("API Response Last 24h:", response.data);
            const total = response.data.reduce((sum, item) => sum + item.count, 0);
            setData((prev) => ({ ...prev, rataRataHarian: Math.round(total / 30) }));
        }).catch((error) => console.error("Error fetching daily average:", error));
    
        // Perubahan dari Hari Sebelumnya
        axios.get("http://localhost:5000/api/vehicle_count/yesterday")
        .then((response) => {
            console.log("API Response Yesterday:", response.data);
            const totalKemarin = response.data.reduce((sum, item) => sum + item.count, 0);
            setData((prev) => {
                const perubahan = prev.totalHariIni - totalKemarin;
                const persentasePerubahan = totalKemarin === 0 ? 0 : Math.round((perubahan / totalKemarin) * 100);
                return { ...prev, perubahanDariKemarin: persentasePerubahan };
            });
        }).catch((error) => console.error("Error fetching vehicle count yesterday:", error));
    
        // Jam Sibuk
        axios.get("http://localhost:5000/api/vehicle_count/history")
        .then((response) => {
            console.log("API Response History:", response.data);
            if (response.data.length > 0) {
                const busiestHour = response.data.reduce((max, item) => item.count > max.count ? item : max, { count: 0 });
                setData((prev) => ({
                    ...prev,
                    jamSibuk: `${busiestHour.hour}:00 - ${busiestHour.hour + 1}:00`,
                    jumlahKendaraanSibuk: busiestHour.count,
                }));
            }
        }).catch((error) => console.error("Error fetching traffic history:", error));
    
    }, []);

    return (
        <DefaultLayout>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {/* Total Kendaraan Hari Ini */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Total Kendaraan Hari Ini</p>
                    <h2 className="text-2xl font-bold">{data.totalHariIni}</h2>
                    <p className="text-sm">Kendaraan</p>
                </div>

                {/* Rata-rata Harian */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Rata-rata Harian</p>
                    <h2 className="text-2xl font-bold">{data.rataRataHarian}</h2>
                    <p className="text-sm">Kendaraan</p>
                </div>

                {/* Perubahan dari Kemarin */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Perubahan dari Kemarin</p>
                    <h2 className="text-2xl font-bold">{data.perubahanDariKemarin}%</h2>
                    <p className="text-sm">{data.perubahanDariKemarin >= 0 ? "Kenaikan" : "Penurunan"}</p>
                </div>

                {/* Jam Sibuk */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Jam Sibuk</p>
                    <h2 className="text-2xl font-bold">{data.jamSibuk}</h2>
                    <p className="text-sm">{data.jumlahKendaraanSibuk} kendaraan</p>
                </div>
            </div>

            {/* Grafik Lalu Lintas */}
            <div className="bg-gray-100 p-6 rounded shadow mb-6">
                <h3 className="text-lg font-semibold mb-4">Grafik Lalu Lintas Harian</h3>
                <div className="h-64 flex items-center justify-center">
                    <p className="text-gray-500">Grafik akan ditampilkan di sini</p>
                </div>
            </div>

            {/* Jenis Kendaraan */}
            <div className="bg-gray-100 p-6 rounded shadow mb-6">
                <h3 className="text-lg font-semibold mb-4">Distribusi Jenis Kendaraan</h3>
                <div className="h-64 flex items-center justify-center">
                    <p className="text-gray-500">Pie chart akan ditampilkan di sini</p>
                </div>
            </div>
        </DefaultLayout>
    );
};

export default Dashboard;