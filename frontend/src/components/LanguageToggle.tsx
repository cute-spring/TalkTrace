import React from 'react'
import { useTranslation } from 'react-i18next'
import { Dropdown, Button } from 'antd'
import { GlobalOutlined } from '@ant-design/icons'
import type { MenuProps } from 'antd'

const LanguageToggle: React.FC<{ collapsed?: boolean }> = ({ collapsed = false }) => {
  const { i18n, t } = useTranslation()

  const handleLanguageChange = (lng: string) => {
    i18n.changeLanguage(lng)
  }

  const currentLanguage = i18n.language

  const menuItems: MenuProps['items'] = [
    {
      key: 'en',
      label: (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '4px 0'
        }}>
          <span>🇺🇸 {t('language.english')}</span>
          {currentLanguage === 'en' && (
            <span style={{
              color: '#1890ff',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              ✓
            </span>
          )}
        </div>
      ),
      onClick: () => handleLanguageChange('en'),
      style: {
        padding: '8px 16px',
        fontSize: '14px',
        borderRadius: '6px',
        margin: '2px 4px',
        transition: 'all 0.2s ease'
      }
    },
    {
      key: 'zh',
      label: (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '4px 0'
        }}>
          <span>🇨🇳 {t('language.chinese')}</span>
          {currentLanguage === 'zh' && (
            <span style={{
              color: '#1890ff',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              ✓
            </span>
          )}
        </div>
      ),
      onClick: () => handleLanguageChange('zh'),
      style: {
        padding: '8px 16px',
        fontSize: '14px',
        borderRadius: '6px',
        margin: '2px 4px',
        transition: 'all 0.2s ease'
      }
    },
  ]

  const getLanguageDisplay = () => {
    switch (currentLanguage) {
      case 'en':
        return t('languageToggle.englishDisplay')
      case 'zh':
        return t('languageToggle.chineseDisplay')
      default:
        return t('languageToggle.englishDisplay')
    }
  }

  if (collapsed) {
    return (
      <div style={{
        padding: '16px',
        textAlign: 'center',
        borderTop: '1px solid #1f1f1f'
      }}>
        <Dropdown
          menu={{ items: menuItems }}
          placement="topRight"
          trigger={['click']}
        >
          <Button
            type="text"
            icon={<GlobalOutlined />}
            style={{
              color: '#fff',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {currentLanguage === 'en' ? t('languageToggle.shortEn') : t('languageToggle.shortZh')}
          </Button>
        </Dropdown>
      </div>
    )
  }

  return (
    <div style={{
      padding: '8px',
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
      borderRadius: '12px',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.15)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
      minWidth: '140px'
    }}>
      <Dropdown
        menu={{
          items: menuItems,
          style: {
            borderRadius: '8px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }
        }}
        placement="topRight"
        trigger={['click']}
      >
        <Button
          type="text"
          icon={<GlobalOutlined style={{ fontSize: '14px', color: '#fff' }} />}
          style={{
            width: '100%',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 12px',
            color: '#fff',
            fontSize: '13px',
            fontWeight: '500',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '8px',
            transition: 'all 0.3s ease',
          }}
          className="language-dropdown-button"
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent'
          }}
        >
          <span style={{ color: '#fff', opacity: 0.9 }}>
            {getLanguageDisplay()}
          </span>
          <span style={{
            fontSize: '10px',
            color: '#fff',
            opacity: 0.6,
            marginLeft: '4px'
          }}>
            ▼
          </span>
        </Button>
      </Dropdown>
    </div>
  )
}

export default LanguageToggle
