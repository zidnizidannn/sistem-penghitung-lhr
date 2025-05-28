import React, { useState, useEffect } from "react";
import DefaultLayout from "../components/defaultLayout";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Button, Dropdown, DropdownItem  } from "flowbite-react";

const DataLhr = () => {
    const [activeView, setActiveView] = useState("daily");
    const [historyData, setHistoryData] = useState([]);
    const [summaryData, setSummaryData] = useState({
        totalKendaraan: 0,
        kendaraanPerJenisData: [],
        grafikData: []
    });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchHistoryData();
    }, [activeView]);

    const api= 'http://localhost:5000/api';

    const fetchHistoryData = async () => {
        setIsLoading(true);
        try {
            let timeSeriesEndpoint = "";
            let summaryEndpoint = "";
            const dateParam = `&date=${selectedDate}`;
    
            if (activeView === "daily") {
                timeSeriesEndpoint = `${api}/vehicle_count/time_series?type=hourly${dateParam}`;
                summaryEndpoint = `${api}/vehicle_count/summary?scope=custom&date=${selectedDate}`;
            } else if (activeView === "weekly") {
                const query = `&year=${selectedYear}&month=${selectedMonth}&week=${selectedWeek}`;
                timeSeriesEndpoint = `${api}/vehicle_count/time_series?type=weekly${query}`;
                summaryEndpoint = `${api}/vehicle_count/summary?scope=custom${query}`;
            } else if (activeView === "monthly") {
                const query = `&year=${selectedMonthlyYear}&month=${selectedMonthlyMonth}`;
                timeSeriesEndpoint = `${api}/vehicle_count/time_series?type=monthly${query}`;
                summaryEndpoint = `${api}/vehicle_count/summary?scope=monthly${query}`;
            }
    
            const timeSeriesRes = await axios.get(timeSeriesEndpoint);
            let processedData = [];
            let grafikData = [];
    
            if (activeView === "daily") {
                processedData = timeSeriesRes.data.map(item => {
                    const total = item.count;
                    return {
                        waktu: `${item.hour.toString().padStart(2, "0")}:00`,
                        jumlah: item.total,
                        motor: item.motor,
                        mobil: item.mobil,
                        bus: item.bus,
                        truk: item.truk,
                        waktuRaw: item.hour
                    };
                }).sort((a, b) => a.waktuRaw - b.waktuRaw);
    
                grafikData = processedData.map(item => ({
                    jam: item.waktu,
                    kendaraan: item.jumlah
                }));
    
            } else if (activeView === "weekly") {
                processedData = timeSeriesRes.data.map(item => {
                    const date = new Date(item.date);
                    const formatDate = date.toLocaleDateString('id-ID', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                    });

                    return { 
                        waktu: formatDate,
                        jumlah: item.total,
                        motor: item.motor,
                        mobil: item.mobil,
                        bus: item.bus,
                        truk: item.truk
                    }
                });

                grafikData = processedData.map(item => ({
                    waktu: item.waktu,
                    jumlah: item.jumlah
                }));
            } else if(activeView === "monthly") {
                processedData = timeSeriesRes.data.map(item => {
                    const day = item.day;
                    
                    return {
                        waktu: `${day.toString().padStart(2, '0')}`,
                        jumlah: item.total,
                        motor: item.motor,
                        mobil: item.mobil,
                        bus: item.bus,
                        truk: item.truk,
                        dayRaw: day
                    };
                });

                grafikData = processedData.map(item => ({
                    waktu: item.waktu,
                    jumlah: item.jumlah
                }));

                console.log("Bulanan grafikData:", grafikData);
            }
    
            const summaryRes = await axios.get(summaryEndpoint);
            const totalKendaraan = summaryRes.data.reduce((sum, item) => sum + item.count, 0);
    
            setHistoryData(processedData);
            setSummaryData({
                totalKendaraan,
                kendaraanPerJenisData: summaryRes.data,
                grafikData
            });
    
        } catch (error) {
            console.error("Error fetching history data:", error);
        } finally {
            setIsLoading(false);
        }
    };    

    const today = new Date();
    const [selectedYear, setSelectedYear] = useState(today.getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1);
    const [selectedWeek, setSelectedWeek] = useState(1);

    const [selectedMonthlyYear, setSelectedMonthlyYear] = useState(today.getFullYear());
    const [selectedMonthlyMonth, setSelectedMonthlyMonth] = useState(today.getMonth() + 1);

    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    useEffect(() => {
        fetchHistoryData();
    }, [activeView, selectedDate, selectedYear, selectedMonth, selectedWeek, selectedMonthlyYear, selectedMonthlyMonth]);   

    return (
        <DefaultLayout>
            <div className="mb-6">
                <div className="flex gap-4 mb-6">
                    <div className="flex bg-gray-200 p-1 rounded-lg w-fit">
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "daily" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("daily")}
                        >
                            Hari Ini
                        </button>
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "weekly" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("weekly")}
                        >
                            Minggu Ini
                        </button>
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "monthly" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("monthly")}
                        >
                            Bulan Ini
                        </button>
                    </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-100 p-4 rounded shadow">
                        <p className="text-sm">Total Kendaraan</p>
                        <h2 className="text-2xl font-bold">{summaryData.totalKendaraan}</h2>
                    </div>
                    
                    <div className="bg-gray-100 p-4 rounded shadow">
                        <p className="text-sm">Jenis Kendaraan Terbanyak</p>
                        <h2 className="text-2xl font-bold">
                            {summaryData.kendaraanPerJenisData.length > 0 
                                ? summaryData.kendaraanPerJenisData.reduce((max, item) => 
                                    item.count > max.count ? item : max, { count: 0 }).vehicle_type 
                                : "-"}
                        </h2>
                        <p className="text-sm">
                            {summaryData.kendaraanPerJenisData.length > 0 
                                ? `${summaryData.kendaraanPerJenisData.reduce((max, item) => 
                                    item.count > max.count ? item : max, { count: 0 }).count} kendaraan` 
                                : ""}
                        </p>
                    </div>
                    
                    <div className="bg-gray-100 p-4 rounded shadow">
                        <p className="text-sm">Rata-rata Kendaraan</p>
                        <h2 className="text-2xl font-bold">
                            {historyData.length > 0 
                                ? Math.round(summaryData.totalKendaraan / historyData.length) 
                                : 0}
                        </h2>
                        <p className="text-sm">
                            {activeView === "daily" && "Per jam"}
                            {activeView === "weekly" && "Per hari"}
                            {activeView === "monthly" && "Per bulan"}
                        </p>
                    </div>
                </div>
                
                <div className="bg-gray-100 p-6 rounded shadow mb-6">
                    <h3 className="text-lg font-semibold mb-4">
                        Grafik
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                        {activeView === "daily" ? (
                            <LineChart data={summaryData.grafikData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="jam" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="kendaraan" stroke="#8884d8" strokeWidth={2} />
                            </LineChart>
                        ) : (
                            <BarChart data={summaryData.grafikData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="waktu" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="jumlah" name="Jumlah Kendaraan" fill="#8884d8" />
                            </BarChart>
                        )}
                    </ResponsiveContainer>
                </div>
                
                <div className="bg-gray-100 p-6 rounded shadow">
                    <h3 className="text-lg font-semibold mb-4">
                        {activeView === "daily" && "Data Lalu Lintas Per Jam"}
                        {activeView === "weekly" && "Data Lalu Lintas 7 Hari Terakhir"}
                        {activeView === "monthly" && `Data Lalu Lintas ${new Date(0, selectedMonthlyMonth - 1).toLocaleString("id-ID", { month: "long" })} ${selectedMonthlyYear}`}
                    </h3>
                    
                    <div className="overflow-x-auto">
                        <table className="min-w-full bg-white">
                            <thead>
                                <tr className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                                    <th className="py-3 px-6 text-left">
                                        {activeView === "daily" && "Jam"}
                                        {activeView === "weekly" && "Tanggal"}
                                        {activeView === "monthly" && "Bulan"}
                                    </th>
                                    <th className="py-3 px-6 text-left">Jumlah Kendaraan</th>
                                    <th className="py-3 px-6 text-left">Motor</th>
                                    <th className="py-3 px-6 text-left">Mobil</th>
                                    <th className="py-3 px-6 text-left">Bus</th>
                                    <th className="py-3 px-6 text-left">Truk</th>
                                </tr>
                            </thead>
                            <tbody className="text-gray-600 text-sm">
                                {isLoading ? (
                                    <tr>
                                        <td colSpan="5" className="py-3 px-6 text-center">Memuat data...</td>
                                    </tr>
                                ) : historyData.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" className="py-3 px-6 text-center">Tidak ada data</td>
                                    </tr>
                                ) : (
                                    historyData.map((item, index) => (
                                        <tr key={index} className="border-b border-gray-200 hover:bg-gray-100">
                                            <td className="py-3 px-6 text-left">{item.waktu}</td>
                                            <td className="py-3 px-6 text-left">{item.jumlah}</td>
                                            <td className="py-3 px-6 text-left">{item.motor}</td>
                                            <td className="py-3 px-6 text-left">{item.mobil}</td>
                                            <td className="py-3 px-6 text-left">{item.bus}</td>
                                            <td className="py-3 px-6 text-left">{item.truk}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DefaultLayout>
    );
};

export default DataLhr;