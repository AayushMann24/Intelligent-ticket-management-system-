import MainLayout from "../layouts/MainLayout";

export default function SettingsPage() {
    return (
        <MainLayout>

            <h1 className="text-3xl font-bold text-white mb-8">
                Settings
            </h1>

            <div className="space-y-6">

                <div className="bg-slate-900 rounded-xl p-6">

                    <h2 className="text-xl font-semibold text-white">
                        Theme
                    </h2>

                    <p className="text-slate-400 mt-2">
                        Dark Mode Enabled
                    </p>

                </div>

                <div className="bg-slate-900 rounded-xl p-6">

                    <h2 className="text-xl font-semibold text-white">
                        Notifications
                    </h2>

                    <label className="flex items-center gap-3 mt-4">

                        <input type="checkbox" defaultChecked />

                        <span className="text-white">
                            Enable Notifications
                        </span>

                    </label>

                </div>

                <div className="bg-slate-900 rounded-xl p-6">

                    <h2 className="text-xl font-semibold text-white">
                        Account
                    </h2>

                    <button
                        className="mt-4 bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg text-white"
                        onClick={()=>{
                            localStorage.removeItem("token");
                            window.location.href="/";
                        }}
                    >
                        Logout
                    </button>

                </div>

            </div>

        </MainLayout>
    );
}