#region File Description
//-----------------------------------------------------------------------------
// Game.cs
//
// Microsoft XNA Community Game Platform
// Copyright (C) Microsoft Corporation. All rights reserved.
//-----------------------------------------------------------------------------
#endregion

#region Using Statements
using System;
using System.Threading;
using System.Globalization;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
#endregion

namespace OpenCity
{
    /// <summary>
    /// Sample showing how to manage different game states, with transitions
    /// between menu screens, a loading screen, the game itself, and a pause
    /// menu. This main game class is extremely simple: all the interesting
    /// stuff happens in the ScreenManager component.
    /// </summary>
    public class OpenCityGame : Microsoft.Xna.Framework.Game
    {
        #region Fields

        GraphicsDeviceManager graphics;
        ScreenManager screenManager;

        #endregion
        
        #region Initialization

        /// <summary>
        /// The main game constructor.
        /// </summary>
        public OpenCityGame()
        {
            Content.RootDirectory = "Content";

            graphics = new GraphicsDeviceManager(this);

            bool fullscreenMode = false;

            if (fullscreenMode == true)
            {
                graphics.PreferredBackBufferWidth = 1440;
                graphics.PreferredBackBufferHeight = 900;
            }
            else
            {
                graphics.PreferredBackBufferWidth = 1024;
                graphics.PreferredBackBufferHeight = 768;                
            }

            graphics.IsFullScreen = fullscreenMode;


            Thread.CurrentThread.CurrentUICulture = Thread.CurrentThread.CurrentCulture;
            DateTime MyDate = System.DateTime.Now;

            // Create the screen manager components.
            screenManager = new ScreenManager(this);            
            Components.Add(screenManager);

            // Activate the first screens.
            screenManager.AddScreen(new BackgroundScreen(), null);
            screenManager.AddScreen(new MainMenuScreen(), null);

            //Console.WriteLine(Thread.CurrentThread.CurrentCulture.TwoLetterISOLanguageName);

            int i = 1000000;
            Console.WriteLine(" " + i.ToString("C"));

            

            foreach (var item in CultureInfo.GetCultures(CultureTypes.UserCustomCulture))
            {
                Console.WriteLine(item.DisplayName);
            }
                        
            Console.WriteLine(MyDate.ToLongDateString());
        }

        #endregion

        #region Draw

        /// <summary>
        /// This is called when the game should draw itself.
        /// </summary>
        protected override void Draw(GameTime gameTime)
        {

            graphics.GraphicsDevice.Clear(Color.Black);

            // The real drawing happens inside the screen manager component.
            base.Draw(gameTime);
        }

        #endregion
    }



    #region Entry Point

    /// <summary>
    /// The main entry point for the application.
    /// </summary>
    static class Program
    {
        static void Main()
        {
            using (OpenCityGame game = new OpenCityGame())
            {
                game.Run();
            }
        }
    }

    #endregion
}
