import localFont from 'next/font/local';

// Define the font once
export const darkerGrotesque = localFont({
  src: '../../public/DarkerGrotesque-Regular.ttf',
  variable: '--font-darker-grotesque',
});

// Pattanakarn font
export const pattanakarn = localFont({
  src: '../../public/Pattanakarn_Regular.ttf',
  variable: '--font-pattanakarn',
});

// Add any additional fonts here
// export const anotherFont = localFont({
//   src: '../../public/AnotherFont.ttf',
//   variable: '--font-another-font',
// }); 