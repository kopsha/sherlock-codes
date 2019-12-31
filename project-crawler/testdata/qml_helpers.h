#ifndef QML_HELPERS_H
#define QML_HELPERS_H

#define PROPERTY(type, name) \
    Q_PROPERTY(type name READ name WRITE set##name NOTIFY name##Changed) \
    private: \
        type m_##name; \
    public: \
        type name() const { return m_##name; } \
        void set##name(type val) { \
            if(val != m_##name) { \
                m_##name = val; \
                emit name##Changed(m_##name); \
            } \
        } \
        Q_SIGNAL void name##Changed(type val); \
        \


#define PROPERTY_READ_ONLY(type, name) \
    Q_PROPERTY(type name READ name NOTIFY name##Changed) \
    private: \
        type m_##name; \
    public: \
        type name() const { return m_##name; } \
        Q_SIGNAL void name##Changed(type val); \
        \

#endif // QML_HELPERS_H
