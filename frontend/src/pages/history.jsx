import React, { useState, useEffect } from "react";
import DefaultLayout from "../components/defaultLayout";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Button, Dropdown, DropdownItem  } from "flowbite-react";
import DownloadButton from "../components/button";

const History = () => {
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

    const fetchHistoryData = async () => {
        setIsLoading(true);
        try {
            let timeSeriesEndpoint = "";
            let summaryEndpoint = "";

            if (activeView === "daily") {
                timeSeriesEndpoint = "http://localhost:5000/api/vehicle_count/time_series?type=hourly";
                summaryEndpoint = "http://localhost:5000/api/vehicle_count/summary?scope=today";
            } else if (activeView === "weekly") {
                timeSeriesEndpoint = "http://localhost:5000/api/vehicle_count/time_series?type=history";
                summaryEndpoint = "http://localhost:5000/api/vehicle_count/summary?scope=all";
            } else if (activeView === "monthly") {
                timeSeriesEndpoint = "http://localhost:5000/api/vehicle_count/time_series?type=history";
                summaryEndpoint = "http://localhost:5000/api/vehicle_count/summary?scope=all";
            }

            const timeSeriesRes = await axios.get(timeSeriesEndpoint);
            
            let processedData = [];
            let grafikData = [];
            
            if (activeView === "daily") {
                processedData = timeSeriesRes.data.map(item => ({
                    waktu: `${item.hour.toString().padStart(2, "0")}:00`,
                    jumlah: item.count,
                    waktuRaw: item.hour
                })).sort((a, b) => a.waktuRaw - b.waktuRaw);
                
                grafikData = processedData.map(item => ({
                    jam: item.waktu,
                    kendaraan: item.jumlah
                }));
            } else if (activeView === "weekly") {
                const grouped = timeSeriesRes.data.reduce((acc, item) => {
                    const date = item.date;
                    if (!acc[date]) acc[date] = { date, count: 0 };
                    acc[date].count += item.count;
                    return acc;
                }, {});
                
                const last7Days = Object.values(grouped)
                    .sort((a, b) => new Date(b.date) - new Date(a.date))
                    .slice(0, 7)
                    .reverse();
                
                processedData = last7Days.map(item => ({
                    waktu: new Date(item.date).toLocaleDateString('id-ID', { weekday: 'short', day: 'numeric', month: 'short' }),
                    jumlah: item.count,
                    waktuRaw: new Date(item.date).getTime()
                }));
                
                grafikData = processedData;
            } else if (activeView === "monthly") {
                const grouped = timeSeriesRes.data.reduce((acc, item) => {
                    const date = new Date(item.date);
                    const monthYear = `${date.getFullYear()}-${date.getMonth()+1}`;
                    if (!acc[monthYear]) {
                        acc[monthYear] = { 
                            month: date.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' }),
                            count: 0,
                            monthIndex: date.getMonth(),
                            year: date.getFullYear()
                        };
                    }
                    acc[monthYear].count += item.count;
                    return acc;
                }, {});
                
                processedData = Object.values(grouped)
                    .sort((a, b) => {
                        if (a.year !== b.year) return a.year - b.year;
                        return a.monthIndex - b.monthIndex;
                    })
                    .slice(-12)
                    .map(item => ({
                        waktu: item.month,
                        jumlah: item.count
                    }));
                
                grafikData = processedData;
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

    const handleDownload = (type, format) => {
        const url = `http://localhost:5000/api/vehicle_count/download?type=${type}&format=${format}`;
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', '');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };    

    return (
        <DefaultLayout>
            <div className="mb-6">
                <div className="flex gap-4 mb-6">
                    <div className="flex bg-gray-200 p-1 rounded-lg w-fit">
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "daily" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("daily")}
                        >
                            Harian
                        </button>
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "weekly" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("weekly")}
                        >
                            Mingguan
                        </button>
                        <button 
                            className={`px-4 py-2 rounded-md ${activeView === "monthly" ? "bg-white shadow" : ""} cursor-pointer`}
                            onClick={() => setActiveView("monthly")}
                        >
                            Bulanan
                        </button>
                    </div>

                    <div className="flex p-1 rounded-lg w-fit gap-4">
                        <Dropdown label="Download CSV" color="green">
                            <DropdownItem onClick={()=> handleDownload("daily", "csv")}>Data Harian</DropdownItem>
                            <DropdownItem onClick={()=> handleDownload("weekly", "csv")}>Data Mingguan</DropdownItem>
                            <DropdownItem onClick={()=> handleDownload("monthly", "csv")}>Data Bulanan</DropdownItem>
                        </Dropdown>

                        <Dropdown label="Download pdf" color="green">
                            <DropdownItem onClick={()=> handleDownload("daily", "pdf")}>Data Harian</DropdownItem>
                            <DropdownItem onClick={()=> handleDownload("weekly", "pdf")}>Data Mingguan</DropdownItem>
                            <DropdownItem onClick={()=> handleDownload("monthly", "pdf")}>Data Bulanan</DropdownItem>
                        </Dropdown>
                    </div>

                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-100 p-4 rounded shadow">
                        <p className="text-sm">Total Kendaraan</p>
                        <h2 className="text-2xl font-bold">{summaryData.totalKendaraan}</h2>
                        <p className="text-sm">
                            {activeView === "daily" && "Hari ini"}
                            {activeView === "weekly" && "Minggu ini"}
                            {activeView === "monthly" && "Bulan ini"}
                        </p>
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
                        {activeView === "daily" && "Grafik Lalu Lintas Hari Ini"}
                        {activeView === "weekly" && "Grafik Lalu Lintas 7 Hari Terakhir"}
                        {activeView === "monthly" && "Grafik Lalu Lintas Bulanan"}
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
                        {activeView === "monthly" && "Data Lalu Lintas Bulanan"}
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
                                    {activeView === "daily" && (
                                        <>
                                            <th className="py-3 px-6 text-left">Motor</th>
                                            <th className="py-3 px-6 text-left">Mobil</th>
                                            <th className="py-3 px-6 text-left">Truk/Bus</th>
                                        </>
                                    )}
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
                                            {activeView === "daily" && (
                                                <>
                                                    <td className="py-3 px-6 text-left">
                                                        {Math.round(item.jumlah * 0.6)}
                                                    </td>
                                                    <td className="py-3 px-6 text-left">
                                                        {Math.round(item.jumlah * 0.3)}
                                                    </td>
                                                    <td className="py-3 px-6 text-left">
                                                        {Math.round(item.jumlah * 0.1)}
                                                    </td>
                                                </>
                                            )}
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

export default History;