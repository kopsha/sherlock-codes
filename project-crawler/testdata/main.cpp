#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QObject>
#include <QtQml>
#include <QtWebView>

#include "logsmanager.h"
#include "specializedscreenmapping.h"
#include "screenframework/screenframework.h"
#include "screenframework/screenmanager.h"
#include "styles.h"
#include "apis/apis.h"
#include "appfilesystemapi.h"

#include "bikeregistration.h"

int main(int argc, char *argv[])
{
    apis::initMetaTypes();
    // Logs manager should be initialized first so it can catch all error messages
    LogsManager::instance().initialize();
    if(APP_LOG_LEVEL == 3)
    {
        QLoggingCategory::setFilterRules(QStringLiteral("qt.bluetooth* = true"));
    }

    apis::AppFileSystemAPI::instance();

    QGuiApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QGuiApplication app(argc, argv);
    QtWebView::initialize();

    QGuiApplication::setFont(dynamic_cast<Styles*>(Styles::instance())->font());

    SpecializedScreenMapping *screenMapping = dynamic_cast<SpecializedScreenMapping*>(SpecializedScreenMapping::instance());
    Q_ASSERT(screenMapping);
    screenframework::initScreenMapping(screenMapping);
    screenframework::initQMLTypes();

    QQmlApplicationEngine engine;

    apis::initAPIS(engine);

    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));

    {

    return app.exec();
}
