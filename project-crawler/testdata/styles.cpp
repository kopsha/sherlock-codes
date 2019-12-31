#include "styles.h"

#include <QGuiApplication>
#include <QScreen>
#include <QFontDatabase>
#include <QFileInfo>
#include <QDir>

Styles *Styles::s_instance = Q_NULLPTR;

Styles::Styles()
    : QQuickItem()
    // colors
    , m_crimson("#ed1c24")
    , m_milanoRed("#b80906")
    , m_milanoRedTransparent("#3fb80906")
    , m_darkRed("#8b0000")
    , m_lightGreen("#63be00")
    , m_darkGreen("#448000")
    , m_black("#000000")
    , m_offBlack("#020202")
    , m_onyx("#121212")
    , m_ironsideGrey("#212121")
    , m_middleGrey("#666666")
    , m_lightGrey("#999999")
    , m_offWhite("#e0e0e0")
    , m_white("#ffffff")
    , m_transparent("transparent")
    , m_yellow("#ffaa1d")

    // margins and component sizes
    , m_marginExtraLarge(48)
    , m_marginLarge(21)
    , m_marginSmall(10)
    , m_rideUnitLeftMargin(2)
    , m_rideBtnSize(20)
    , m_rideIconSize(16)
    , m_mapSnapshotSize(70)
    , m_separatorSize(1)
    , m_redSeparatorSize(8)
    , m_sliderHeight(2)
    , m_sliderHandleSize(32)
    , m_sliderHandleBorderSize(2)
    , m_sliderTickmarkSize(10)
    , m_tuneIconSize(24)
    , m_comboBoxSize(24)
    , m_switchSize(48)
    , m_arrowSize(10)
    , m_logoSize(45)
    , m_connectionHeight(56)
    , m_connectionBikeSize(40)
    , m_connectionBatterySize(20)
    , m_dashboardIconSize(90)
    , m_closeIconSize(16)
    , m_diagnoseHealthIconSize(50)
    , m_comboBoxHeight(40)
    , m_marginTop(80)
    , m_checkBoxSize(24)
    , m_checkBoxMarkSize(16)
    // text sizes
    , m_extraLarge(70)
    , m_h1(48)
    , m_h2(36)
    , m_h3(24)
    , m_h4(16)
    , m_h5(8)
    , m_p1(18)
    , m_p2(14)
    , m_p3(12)
    , m_p4(10)
    // fonts styles
    , m_condBold("CondBold")
    , m_light("Light")
    , m_defaultCondRegular("CondRegular")
    , m_medium("Medium")
    , m_regular("Regular")

    , m_backgroundColor("#202020")
    , m_headerColor("#2C3539")
    , m_textColor("#ffffff")
    , m_defaultTextColor("#f0f0f0")
    , m_colorControl("red")
    , m_colorControlInactive("#2C3539")
    , m_colorControlPressed("#7f0000")

    , m_textPointSize(15)
    , m_imageLabelSize(30)
    , m_textTitlePointSize(30)
    , m_widthPercentWideItem(0.8)

    , m_heightTopToolBar(66)
    , m_heightBtnTopToolBar(24)
    , m_textPointSizeTitleTopToolBar(25)

    , m_heightFooterLetsRide(60)
    , m_heightBtnFooterLetsRide(50)
    , m_diameterBtnStartNavigateLetsRide(70)

    , m_greyTransparent("#C8505050")
    , m_devicePixelRatio(QGuiApplication::screens().at(0)->devicePixelRatio())

    , m_iOSKeyboardHeight(258)
    , m_gridUnitSize(8)
    , m_diagnoseSmallIconSize(16)
    , m_diagnoseRightArrowLinkIconSize(16)
    , m_thinBorder(2)
    , m_mapLineWidth(3)
    , m_veryThinBorder(1)
    , m_footerHeight(56)
    , m_popupImageSize(40)
{
    QDir fontDir(":/res/fonts");
    foreach (QFileInfo fileInfo, fontDir.entryInfoList())
    {
        QFontDatabase::addApplicationFont(fileInfo.absoluteFilePath());
    }

    m_font = QFont("DINOT");
    m_font.setStyleName(m_defaultCondRegular);
    qApp->setFont(m_font);
}

QObject* Styles::instance(QQmlEngine*, QJSEngine*)
{
    if (Q_NULLPTR == s_instance)
    {
        s_instance = new Styles;
    }
    return s_instance;
}
