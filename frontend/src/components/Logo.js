import React from 'react';

const Logo = ({ collapsed }) => {
  const logoStyle = {
    height: '32px',
    margin: '16px',
    textAlign: 'center',
    color: 'white',
    fontSize: collapsed ? '14px' : '18px',
    fontWeight: 'bold',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    transition: 'all 0.3s',
  };

  return (
    <div style={logoStyle}>
      {collapsed ? 'FR' : 'Fitness Reservation'}
    </div>
  );
};

export default Logo;