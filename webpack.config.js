const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: {
    popup: './public/index.jsx'  // Update the entry point to .tsx if using TypeScript
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.(jsx?|tsx?)$/,  // Handle .ts and .tsx files
        exclude: /node_modules/,
        use: 'babel-loader'
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.tsx?$/,  // Add ts-loader for TypeScript files
        exclude: /node_modules/,
        use: 'ts-loader'
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx']  // Add .ts and .tsx extensions
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
      filename: 'popup.html',
      chunks: ['popup']
    })
  ]
};
