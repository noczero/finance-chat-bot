
export default function Header(){
    return (
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">
                    {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
                    <a href="/">
                        Financial Assistant
                    </a>
                </h1>
              </div>
            </div>
          </div>
        </header>
    )
};