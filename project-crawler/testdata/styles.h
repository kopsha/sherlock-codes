#ifndef STYLES_H
#define STYLES_H

#include <QQuickItem>
#include <QColor>
#include <QFont>

#include "qml_helpers.h"

class Styles : public QQuickItem
{
    Q_OBJECT
    Q_DISABLE_COPY(Styles)

    PROPERTY(QColor, crimson)
    PROPERTY(QColor, milanoRed)
    PROPERTY(QColor, milanoRedTransparent)
    PROPERTY(QColor, darkRed)
    PROPERTY(QColor, lightGreen)
    PROPERTY(QColor, darkGreen)
    PROPERTY(QColor, black)
    PROPERTY(QColor, offBlack)
    PROPERTY(QColor, onyx)
    PROPERTY(QColor, ironsideGrey)
    PROPERTY(QColor, middleGrey)
    PROPERTY(QColor, lightGrey)
    PROPERTY(QColor, offWhite)
    PROPERTY(QColor, white)
    PROPERTY(QColor, transparent)
    PROPERTY(QColor, yellow)

    PROPERTY(int, marginExtraLarge)
    PROPERTY(int, marginLarge)
    PROPERTY(int, marginSmall)
    PROPERTY(int, rideUnitLeftMargin)
    PROPERTY(int, rideBtnSize)
    PROPERTY(int, rideIconSize)
    PROPERTY(int, mapSnapshotSize)
    PROPERTY(int, separatorSize)
    PROPERTY(int, redSeparatorSize)
    PROPERTY(int, sliderHeight)
    PROPERTY(int, sliderHandleSize)
    PROPERTY(int, sliderHandleBorderSize)
    PROPERTY(int, sliderTickmarkSize)
    PROPERTY(int, tuneIconSize)
    PROPERTY(int, comboBoxSize)
    PROPERTY(int, switchSize)
    PROPERTY(int, arrowSize)
    PROPERTY(int, logoSize)
    PROPERTY(int, connectionHeight)
    PROPERTY(int, connectionBikeSize)
    PROPERTY(int, connectionBatterySize)
    PROPERTY(int, dashboardIconSize)
    PROPERTY(int, closeIconSize)
    PROPERTY(int, diagnoseHealthIconSize)
    PROPERTY(int, comboBoxHeight)
    PROPERTY(int, marginTop)
    PROPERTY(int, checkBoxSize)
    PROPERTY(int, checkBoxMarkSize)

    PROPERTY(int, extraLarge)
    PROPERTY(int, h1)
    PROPERTY(int, h2)
    PROPERTY(int, h3)
    PROPERTY(int, h4)
    PROPERTY(int, h5)

    PROPERTY(int, p1)
    PROPERTY(int, p2)
    PROPERTY(int, p3)
    PROPERTY(int, p4)

    PROPERTY(QString, condBold)
    PROPERTY(QString, light)
    PROPERTY(QString, defaultCondRegular)
    PROPERTY(QString, medium)
    PROPERTY(QString, regular)

    PROPERTY(QColor, backgroundColor)
    PROPERTY(QColor, headerColor)
    PROPERTY(QColor, textColor)
    PROPERTY(QColor, defaultTextColor)
    PROPERTY(QColor, colorControl)
    PROPERTY(QColor, colorControlInactive)
    PROPERTY(QColor, colorControlPressed)

    PROPERTY(int, textPointSize)
    PROPERTY(int, imageLabelSize)
    PROPERTY(int, textTitlePointSize)
    PROPERTY(double, widthPercentWideItem)

    PROPERTY(int, heightTopToolBar)
    PROPERTY(int, heightBtnTopToolBar)
    PROPERTY(int, textPointSizeTitleTopToolBar)

    PROPERTY(int, heightFooterLetsRide)
    PROPERTY(int, heightBtnFooterLetsRide)
    PROPERTY(int, diameterBtnStartNavigateLetsRide)

    PROPERTY(QColor, greyTransparent)
    PROPERTY(qreal, devicePixelRatio)

    PROPERTY(int, iOSKeyboardHeight)

    PROPERTY(QFont, font)

    PROPERTY(int, gridUnitSize)

    PROPERTY(int, diagnoseSmallIconSize)
    PROPERTY(int, diagnoseRightArrowLinkIconSize)

    PROPERTY(int, thinBorder)
    PROPERTY(int, mapLineWidth)
    PROPERTY(int, veryThinBorder)

    PROPERTY(int, footerHeight)
    PROPERTY(int, popupImageSize)

public:
    static QObject* instance(QQmlEngine* en = Q_NULLPTR, QJSEngine* jse = Q_NULLPTR);

private:
    Styles();
    static Styles* s_instance;

};

#endif // STYLES_H
