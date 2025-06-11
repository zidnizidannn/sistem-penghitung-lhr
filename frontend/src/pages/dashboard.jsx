import React, { useState, useEffect } from "react";
import DefaultLayout from "../components/defaultLayout";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const Dashboard = () => {  
    const [data, setData] = useState({
        totalHariIni: 0,
        rataRataHariIni: 0,
        perubahanDariKemarin: 0,
        jamSibuk: "00:00 - 00:00",
        jumlahKendaraanSibuk: 0,
        grafikData: []
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                // total kendaraan hari ini
                const todayRes = await axios.get("http://localhost:5000/api/vehicle_count/summary?scope=today");
                const totalHariIni = todayRes.data.reduce((sum, item) => sum + (item.smp || 0), 0);
    
                // total kendaraan kemarin
                const yesterdayRes = await axios.get("http://localhost:5000/api/vehicle_count/summary?scope=yesterday");
                const totalKemarin = yesterdayRes.data.reduce((sum, item) => sum + (item.smp || 0), 0);
    
                // data grafik per jam hari ini
                const grafikRes = await axios.get("http://localhost:5000/api/vehicle_count/time_series?type=hourly");
                const grafikData = Array.isArray(grafikRes.data)
                    ? grafikRes.data
                        .filter(item => item.hour !== undefined)
                        .map(item => ({
                        jam: `${item.hour.toString().padStart(2, "0")}:00`,
                        smp: item.total ?? 0
                    }))
                : [];
    
                // rata-rata kendaraan per jam hari ini
                const now = new Date();
                const jamBerjalan = now.getHours() + 1;
                const rataRataHariIni = Math.round(totalHariIni / jamBerjalan);
    
                // perubahan dari kemarin
                const perubahan = totalHariIni - totalKemarin;
                const persentasePerubahan = totalKemarin === 0 ? 0 : Math.round((perubahan / totalKemarin) * 100);
    
                // data historis (per 15 menit) untuk cari jam sibuk
                const hourlyRes = await axios.get("http://localhost:5000/api/vehicle_count/time_series?type=hourly");
                const hourlyData = hourlyRes.data;

                let jamSibuk = "00:00 - 00:00";
                let jumlahKendaraanSibuk = 0;

                if (hourlyData.length > 0) {
                    const busiest = hourlyData.reduce((max, item) =>
                        item.smp > max.smp ? item : max,
                        { smp: 0, hour: 0 }
                    );
                    const hourStr = busiest.hour.toString().padStart(2, "0");
                    const nextHourStr = (busiest.hour + 1).toString().padStart(2, "0");
                    jamSibuk = `${hourStr}:00 - ${nextHourStr}:00`;
                    jumlahKendaraanSibuk = busiest.count;
                }
    
                setData({
                    totalHariIni,
                    rataRataHariIni,
                    perubahanDariKemarin: persentasePerubahan,
                    jamSibuk,
                    jumlahKendaraanSibuk,
                    grafikData
                });
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        };
        fetchData();
    }, []);

    return (
        <DefaultLayout>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {/* Total Kendaraan Hari Ini */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Total Kendaraan Hari Ini</p>
                    <h2 className="text-2xl font-bold">{data.totalHariIni}</h2>
                    <p className="text-sm">SMP/Jam</p>
                </div>

                {/* Rata-rata Kendaraan Melintas Hari Ini */}
                <div className="bg-gray-100 p-4 rounded shadow">
                    <p className="text-sm">Rata-rata Kendaraan Melintas Hari Ini</p>
                    <h2 className="text-2xl font-bold">{data.rataRataHariIni}</h2>
                    <p className="text-sm">Kendaraan per jam</p>
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

            <div className="bg-gray-100 p-6 rounded shadow mb-6">
                <h3 className="text-lg font-semibold mb-4">Grafik Lalu Lintas Hari Ini</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.grafikData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="jam" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="smp" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </DefaultLayout>
    );
};

export default Dashboard;