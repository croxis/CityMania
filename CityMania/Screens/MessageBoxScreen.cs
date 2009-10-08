#region Using Statements

// System
using System;

// XNA
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;

#endregion

namespace CityMania
{
    /// <summary>
    /// A popup message box screen, used to display "are you sure?"
    /// confirmation messages.
    /// </summary>
    class MessageBoxScreen : GameScreen
    {
        #region Fields

        string message;
        Texture2D blankTexture;
        
        // Dialog Content
        Rectangle dialogContentRectangle = new Rectangle(0, 0, 200, 80);

        // Dialog Textures
        Texture2D bgTopTexture;
        Texture2D bgBottomTexture;
        Texture2D bgLeftTexture;
        Texture2D bgRightTexture;

        Texture2D bgTopLeftTexture;
        Texture2D bgTopRightTexture;
        Texture2D bgBottomLeftTexture;
        Texture2D bgBottomRightTexture;

        #endregion

        #region Events

        public event EventHandler<PlayerIndexEventArgs> Accepted;
        public event EventHandler<PlayerIndexEventArgs> Cancelled;

        #endregion

        #region Initialization


        /// <summary>
        /// Constructor automatically includes the standard "A=ok, B=cancel"
        /// usage text prompt.
        /// </summary>
        public MessageBoxScreen(string message)
            : this(message, true)
        { }


        /// <summary>
        /// Constructor lets the caller specify whether to include the standard
        /// "A=ok, B=cancel" usage text prompt.
        /// </summary>
        public MessageBoxScreen(string message, bool includeUsageText)
        {
            const string usageText = "\nEnter = ok" +
                                     "\nEsc = cancel"; 
            
            if (includeUsageText)
                this.message = message + usageText;
            else
                this.message = message;

            IsPopup = true;

            this.message = "Dialog Title";

            //TransitionOnTime = TimeSpan.FromSeconds(0.2);
            //TransitionOffTime = TimeSpan.FromSeconds(0.2);
        }


        /// <summary>
        /// Loads graphics content for this screen. This uses the shared ContentManager
        /// provided by the Game class, so the content will remain loaded forever.
        /// Whenever a subsequent MessageBoxScreen tries to load this same content,
        /// it will just get back another reference to the already loaded data.
        /// </summary>
        public override void LoadContent()
        {
            ContentManager content = ScreenManager.Game.Content;

            // Default Dialog
            bgTopTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgTop");
            bgBottomTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgBottom");
            bgLeftTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgLeft");
            bgRightTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgRight");

            bgTopLeftTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgTopLeft");
            bgTopRightTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgTopRight");
            bgBottomLeftTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgBottomLeft");
            bgBottomRightTexture = content.Load<Texture2D>(@"Images\GUI\Dialogs\Normal\bgBottomRight");

            blankTexture = content.Load<Texture2D>(@"blank");
        }


        #endregion

        #region Handle Input


        /// <summary>
        /// Responds to user input, accepting or cancelling the message box.
        /// </summary>
        public override void HandleInput(InputState input)
        {
            PlayerIndex playerIndex;

            // We pass in our ControllingPlayer, which may either be null (to
            // accept input from any player) or a specific index. If we pass a null
            // controlling player, the InputState helper returns to us which player
            // actually provided the input. We pass that through to our Accepted and
            // Cancelled events, so they can tell which player triggered them.
            if (input.IsMenuSelect(ControllingPlayer, out playerIndex))
            {
                // Raise the accepted event, then exit the message box.
                if (Accepted != null)
                    Accepted(this, new PlayerIndexEventArgs(playerIndex));

                ExitScreen();
            }
            else if (input.IsMenuCancel(ControllingPlayer, out playerIndex))
            {
                // Raise the cancelled event, then exit the message box.
                if (Cancelled != null)
                    Cancelled(this, new PlayerIndexEventArgs(playerIndex));

                ExitScreen();
            }
        }


        #endregion

        #region Draw


        /// <summary>
        /// Draws the message box.
        /// </summary>
        public override void Draw(GameTime gameTime)
        {
            SpriteBatch spriteBatch = ScreenManager.SpriteBatch;
            SpriteFont font = ScreenManager.Font;

            // Darken down any other screens that were drawn beneath the popup.
            //ScreenManager.FadeBackBufferToBlack(TransitionAlpha * 2 / 3);

            // Center the message text in the viewport.
            Viewport viewport = ScreenManager.GraphicsDevice.Viewport;
            Vector2 viewportSize = new Vector2(viewport.Width, viewport.Height);
            Vector2 textSize = font.MeasureString(message);
            Vector2 contentSize = new Vector2(dialogContentRectangle.Width,dialogContentRectangle.Height);
            
            Vector2 dialogPosition = (viewportSize - contentSize) / 2;
            Vector2 textPosition = dialogPosition;


            // Padding.
            const int hPad = 11;
            const int vPad = 5;

            Rectangle dialogRectangle = new Rectangle((int)dialogPosition.X - hPad,
                                                        (int)dialogPosition.Y - vPad,
                                                        (int)dialogContentRectangle.Width + hPad * 2,
                                                        (int)dialogContentRectangle.Height + vPad * 2);

            // Top
            Rectangle bgTopLeftRectangle = new Rectangle((int)dialogRectangle.X,
                                                        (int)dialogRectangle.Y,
                                                        (int)bgTopLeftTexture.Width,
                                                        (int)bgTopLeftTexture.Height);

            Rectangle bgTopRightRectangle = new Rectangle((int)dialogRectangle.X + (dialogRectangle.Width) - bgTopRightTexture.Width,
                                                        (int)dialogRectangle.Y,
                                                        (int)bgTopRightTexture.Width,
                                                        (int)bgTopRightTexture.Height);

            Rectangle bgTopRectangle = new Rectangle((int)dialogRectangle.X + bgTopLeftTexture.Width,
                                                        (int)dialogRectangle.Y,
                                                        (int)dialogRectangle.Width - bgTopLeftTexture.Width - bgTopRightTexture.Width,
                                                        (int)bgTopTexture.Height);

            // Bottom
            Rectangle bgBottomLeftRectangle = new Rectangle((int)dialogRectangle.X,
                                                        (int)dialogRectangle.Y + dialogRectangle.Height - bgBottomLeftTexture.Height,
                                                        (int)bgBottomLeftTexture.Width,
                                                        (int)bgBottomLeftTexture.Height);

            Rectangle bgBottomRightRectangle = new Rectangle((int)dialogRectangle.X + (dialogRectangle.Width) - bgBottomRightTexture.Width,
                                                        (int)bgBottomLeftRectangle.Y,
                                                        (int)bgBottomRightTexture.Width,
                                                        (int)bgBottomRightTexture.Height);

            Rectangle bgBottomRectangle = new Rectangle((int)dialogRectangle.X + bgBottomLeftTexture.Width,
                                                        (int)bgBottomLeftRectangle.Y,
                                                        (int)dialogRectangle.Width - bgBottomLeftTexture.Width - bgBottomRightTexture.Width,
                                                        (int)bgBottomTexture.Height);

            // Middle
            Rectangle bgLeftRectangle = new Rectangle((int)dialogRectangle.X,
                                                        (int)dialogRectangle.Y + bgTopRectangle.Height,
                                                        (int)bgLeftTexture.Width,
                                                        (int)dialogRectangle.Height - bgTopTexture.Height - bgBottomTexture.Height);

            Rectangle bgRightRectangle = new Rectangle((int)dialogRectangle.X + (dialogRectangle.Width) - bgRightTexture.Width,
                                                        (int)bgLeftRectangle.Y,
                                                        (int)bgRightTexture.Width,
                                                        (int)bgLeftRectangle.Height);

            Rectangle bgMiddleRectangle = new Rectangle((int)dialogRectangle.X + bgLeftRectangle.Width,
                                                        (int)bgLeftRectangle.Y,
                                                        (int)dialogRectangle.Width - bgLeftRectangle.Width - bgRightRectangle.Width,
                                                        (int)dialogRectangle.Height - bgTopRectangle.Height - bgBottomRectangle.Height);

            // Fade the popup alpha during transitions.
            Color color = new Color(255, 255, 255);

            spriteBatch.Begin();

            // Draw the Dialog
            spriteBatch.Draw(bgTopLeftTexture, bgTopLeftRectangle, color);
            spriteBatch.Draw(bgTopRightTexture, bgTopRightRectangle, color);
            spriteBatch.Draw(bgTopTexture, bgTopRectangle, color);

            spriteBatch.Draw(bgBottomLeftTexture, bgBottomLeftRectangle, color);
            spriteBatch.Draw(bgBottomRightTexture, bgBottomRightRectangle, color);
            spriteBatch.Draw(bgBottomTexture, bgBottomRectangle, color);

            spriteBatch.Draw(bgLeftTexture, bgLeftRectangle, color);
            spriteBatch.Draw(bgRightTexture, bgRightRectangle, color);
            spriteBatch.Draw(blankTexture, bgMiddleRectangle, new Color(156, 178, 194));            

            // Draw the Dialog Title.
            spriteBatch.DrawString(font, message, textPosition, new Color(54, 59, 76));

            spriteBatch.End();
        }


        #endregion
    }
}
